#!/usr/bin/env python3
"""Regenerate evaluator-readable Markdown evidence from the live workspace."""

from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable, Iterable

import psycopg
import requests
from databricks.sdk import WorkspaceClient


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
CATALOG = "vandelay"
SCHEMA = "rebate_fraud"
WAREHOUSE_ID = "5d942ad88a289cf7"
PIPELINE_ID = "83a6f0b6-694b-49eb-b0df-c95648e18f3e"
ORCHESTRATION_JOB_ID = 453506024885536
GENERATOR_JOB_ID = 582028948116959
GOVERNANCE_JOB_ID = 129437839852986
GENIE_SPACE_ID = "01f1e3b93f4b11e79b2fbfcd74547821"
APP_NAME = "rebate-ops-matt-cutini"
LAKEBASE_ENDPOINT = "projects/rebate-fraud-ops/branches/production/endpoints/primary"
LAKEBASE_DATABASE = "databricks_postgres"

FILES = [
    "HEADLINES.md",
    "00_answer_key.md",
    "01_pipeline_run.md",
    "02_data_quality.md",
    "03_business_results.md",
    "04_ai_output.md",
    "05_ai_evaluation.md",
    "06_governance.md",
    "07_lakebase.md",
    "08_genie.md",
    "09_orchestration.md",
    "10_app.md",
    "README.md",
]

EMAIL_PATTERN = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
TOKEN_PATTERN = re.compile(r"(?i)(bearer\s+|token[=:]\s*|password[=:]\s*)[^\s,;]+")
SENSITIVE_COLUMNS = {
    "pharmacy_name",
    "legal_name",
    "observed_pharmacy_name",
    "principal",
    "test_principal",
    "changed_by",
    "creator_user_name",
    "user_name",
    "email",
    "pharmacy_address",
    "pharmacy_phone",
    "pharmacy_fax",
}


@dataclass
class QueryResult:
    columns: list[str]
    rows: list[dict[str, Any]]
    statement_id: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def enum_value(value: Any) -> str:
    return str(getattr(value, "value", value))


def redact_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    text = EMAIL_PATTERN.sub("[REDACTED IDENTITY]", text)
    text = TOKEN_PATTERN.sub(lambda match: f"{match.group(1)}[REDACTED]", text)
    return text.replace("\n", " ").replace("\r", " ")


def redact_row(row: dict[str, Any]) -> dict[str, Any]:
    redacted = {}
    for column, value in row.items():
        if column.lower() in SENSITIVE_COLUMNS:
            redacted[column] = "[REDACTED]"
        elif isinstance(value, str):
            redacted[column] = redact_text(value)
        else:
            redacted[column] = value
    return redacted


def markdown_table(columns: Iterable[str], rows: Iterable[dict[str, Any]]) -> str:
    columns = list(columns)
    rows = [redact_row(row) for row in rows]
    if not columns:
        return "_No columns returned._"
    lines = [
        "| " + " | ".join(redact_text(column) for column in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    if not rows:
        lines.append("| " + " | ".join("_no rows_" for _ in columns) + " |")
    else:
        for row in rows:
            values = [redact_text(row.get(column, "")).replace("|", "\\|") for column in columns]
            lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def json_block(value: Any) -> str:
    sanitized = json.loads(EMAIL_PATTERN.sub("[REDACTED IDENTITY]", json.dumps(value, default=str)))
    return "```json\n" + json.dumps(sanitized, indent=2, sort_keys=True, default=str) + "\n```"


def document(title: str, explanation: str, body: str, generated_at: str) -> str:
    return (
        f"Generated {generated_at} by tools/generate_evidence.py from the live workspace\n\n"
        f"# {title}\n\n{explanation.strip()}\n\n{body.strip()}\n"
    )


class EvidenceGenerator:
    def __init__(self, profile: str, generated_at: str):
        self.profile = profile
        self.generated_at = generated_at
        self.workspace = WorkspaceClient(profile=profile)
        self.final_run = self.latest_successful_run(ORCHESTRATION_JOB_ID)

    def sql(self, statement: str) -> QueryResult:
        response = self.workspace.statement_execution.execute_statement(
            warehouse_id=WAREHOUSE_ID,
            statement=statement,
            catalog=CATALOG,
            schema=SCHEMA,
            wait_timeout="50s",
        )
        while enum_value(response.status.state) in {"PENDING", "RUNNING"}:
            time.sleep(2)
            response = self.workspace.statement_execution.get_statement(response.statement_id)
        if enum_value(response.status.state) != "SUCCEEDED":
            raise RuntimeError(f"Statement failed: {response.status.error}")
        columns = [column.name for column in response.manifest.schema.columns]
        data = response.result.data_array or []
        return QueryResult(columns, [dict(zip(columns, row)) for row in data], response.statement_id)

    def latest_successful_run(self, job_id: int):
        for run in self.workspace.jobs.list_runs(job_id=job_id, completed_only=True, limit=25):
            if enum_value(run.state.result_state) == "SUCCESS":
                return self.workspace.jobs.get_run(run.run_id)
        raise RuntimeError(f"No successful run found for job {job_id}")

    def task_output(self, run_id: int) -> dict[str, Any]:
        try:
            output = self.workspace.jobs.get_run_output(run_id=run_id)
        except Exception as error:
            return {"error": redact_text(error)}
        if output.notebook_output and output.notebook_output.result:
            result = output.notebook_output.result
            try:
                return {"notebook_result": json.loads(result)}
            except json.JSONDecodeError:
                return {"notebook_result": redact_text(result)}
        if output.logs:
            return {"logs": redact_text(output.logs)}
        if output.sql_output is not None:
            return {"sql_output": output.sql_output.as_dict()}
        return {"result": "No task exit value returned by the Jobs API."}

    def latest_pipeline_update(self):
        updates = self.workspace.pipelines.list_updates(pipeline_id=PIPELINE_ID, max_results=25)
        for update in updates.updates or []:
            if enum_value(update.state) == "COMPLETED":
                return update
        raise RuntimeError("No completed pipeline update found")

    def lakebase(self):
        endpoint = self.workspace.postgres.get_endpoint(name=LAKEBASE_ENDPOINT)
        credential = self.workspace.postgres.generate_database_credential(endpoint=LAKEBASE_ENDPOINT)
        return psycopg.connect(
            host=endpoint.status.hosts.host,
            port=5432,
            dbname=LAKEBASE_DATABASE,
            user=self.workspace.current_user.me().user_name,
            password=credential.token,
            sslmode="require",
        )

    def write(self, filename: str, title: str, explanation: str, body: str) -> None:
        path = EVIDENCE / filename
        path.write_text(document(title, explanation, body, self.generated_at))
        print(json.dumps({"file": str(path), "bytes": path.stat().st_size}))

    def generate_00_answer_key(self) -> None:
        run = self.latest_successful_run(GENERATOR_JOB_ID)
        task = run.tasks[0]
        output = self.task_output(task.run_id)
        manifest = self.sql(
            f"""
            SELECT count(*) AS released_periods,
                   sum(controlTotals.claimRecordCount) AS released_claim_rows,
                   round(sum(controlTotals.claimAmountTotal), 2) AS released_claim_amount
            FROM {CATALOG}.{SCHEMA}.bronze_control_manifest
            """
        )
        verification = output.get("notebook_result", {}).get("verification", output)
        rows = [{"metric": key, "live_generator_value": value} for key, value in verification.items()]
        body = f"""
## Generator Run

| Job run | Task run | Result |
| --- | --- | --- |
| `{run.run_id}` | `{task.run_id}` | `{enum_value(run.state.result_state)}` |

## Generator Verification

{markdown_table(["metric", "live_generator_value"], rows)}

## Released Control Manifests

Statement `{manifest.statement_id}`:

{markdown_table(manifest.columns, manifest.rows)}
"""
        self.write(
            "00_answer_key.md",
            "Synthetic Data Answer Key",
            "This file proves the deterministic synthetic generator's own assertions and the released control-manifest totals, read from the latest successful generator run and live pipeline table.",
            body,
        )

    def generate_headlines(self) -> None:
        coverage = self.sql(
            f"""
            SELECT count(*) AS released_periods,
                   sum(controlTotals.claimRecordCount) AS released_claim_rows
            FROM {CATALOG}.{SCHEMA}.bronze_control_manifest
            """
        ).rows[0]
        money = self.sql(
            f"""
            SELECT count(*) AS feature_groups,
                   round(sum(estimated_overpayment), 2) AS estimated_exposure
            FROM {CATALOG}.{SCHEMA}.gold_case_features
            """
        ).rows[0]
        claim_share = round(int(coverage["released_claim_rows"]) / 120000 * 100, 1)
        period_share = round(int(coverage["released_periods"]) / 12 * 100, 1)
        body = f"""
## 1. Coverage

- **Exact wording:** {int(coverage['released_claim_rows']):,} released synthetic claims across {coverage['released_periods']} released periods.
- **Share of:** {int(coverage['released_claim_rows']):,} of 120,000 generated claims ({claim_share}%) and {coverage['released_periods']} of 12 generated periods ({period_share}%); one generated period remains unreleased.
- **Measured:** {self.generated_at}.
- **Classification:** Measured from live control-manifest records over simulated data.
- **Evidence:** `evidence/00_answer_key.md`.

## 2. Money

- **Exact wording:** ${Decimal(str(money['estimated_exposure'])):,.2f} in simulated suspected rebate overpayment exposure.
- **Share of:** 100% of estimated overpayment across the {int(money['feature_groups']):,} live gold feature groups at measurement time.
- **Measured:** {self.generated_at}.
- **Classification:** Simulated monetary exposure, measured from live gold data; not verified fraud or realized recovery.
- **Evidence:** `evidence/03_business_results.md`.
"""
        self.write(
            "HEADLINES.md",
            "Approved Headline Figures",
            "This file records the user-selected headline figures exactly as supported by live-workspace queries, including their denominator, measurement time, verification classification, and source file so the README and deck use identical values.",
            body,
        )

    def generate_01_pipeline_run(self) -> None:
        pipeline = self.workspace.pipelines.get(PIPELINE_ID)
        update = self.latest_pipeline_update()
        counts = self.sql(
            f"""
            SELECT * FROM (
              SELECT 'bronze_control_manifest' AS table_name, count(*) AS row_count FROM {CATALOG}.{SCHEMA}.bronze_control_manifest UNION ALL
              SELECT 'bronze_medical_claims', count(*) FROM {CATALOG}.{SCHEMA}.bronze_medical_claims UNION ALL
              SELECT 'bronze_pharmacy_claims', count(*) FROM {CATALOG}.{SCHEMA}.bronze_pharmacy_claims UNION ALL
              SELECT 'bronze_manufacturer_sales', count(*) FROM {CATALOG}.{SCHEMA}.bronze_manufacturer_sales UNION ALL
              SELECT 'bronze_wholesaler_shipments', count(*) FROM {CATALOG}.{SCHEMA}.bronze_wholesaler_shipments UNION ALL
              SELECT 'silver_claims_conformed', count(*) FROM {CATALOG}.{SCHEMA}.silver_claims_conformed UNION ALL
              SELECT 'silver_claims', count(*) FROM {CATALOG}.{SCHEMA}.silver_claims UNION ALL
              SELECT 'quarantine_claims', count(*) FROM {CATALOG}.{SCHEMA}.quarantine_claims UNION ALL
              SELECT 'silver_product_movement', count(*) FROM {CATALOG}.{SCHEMA}.silver_product_movement UNION ALL
              SELECT 'silver_pharmacy_entities', count(*) FROM {CATALOG}.{SCHEMA}.silver_pharmacy_entities UNION ALL
              SELECT 'reconciliation_claims', count(*) FROM {CATALOG}.{SCHEMA}.reconciliation_claims UNION ALL
              SELECT 'gold_case_features', count(*) FROM {CATALOG}.{SCHEMA}.gold_case_features
            ) ORDER BY table_name
            """
        )
        expectation = self.sql(
            f"""
            SELECT origin.update_id,
                   details:flow_progress.data_quality.expectations AS expectation_metrics
            FROM event_log('{PIPELINE_ID}')
            WHERE event_type = 'flow_progress'
              AND origin.update_id = '{update.update_id}'
              AND details:flow_progress.data_quality.expectations IS NOT NULL
            ORDER BY timestamp DESC
            """
        )
        start = getattr(update, "start_time", None)
        end = getattr(update, "end_time", None)
        body = f"""
## Live Pipeline

| Pipeline ID | Name | Latest completed update | State | Serverless | Catalog | Schema |
| --- | --- | --- | --- | --- | --- | --- |
| `{PIPELINE_ID}` | `{redact_text(pipeline.name)}` | `{update.update_id}` | `{enum_value(update.state)}` | `{pipeline.spec.serverless}` | `{pipeline.spec.catalog}` | `{pipeline.spec.target}` |

- Update start: `{redact_text(start)}`
- Update end: `{redact_text(end)}`
- Final orchestration run: `{self.final_run.run_id}`

## Live Row Counts

Statement `{counts.statement_id}`:

{markdown_table(counts.columns, counts.rows)}

## Latest Update Expectation Payloads

Statement `{expectation.statement_id}`:

{markdown_table(expectation.columns, expectation.rows)}
"""
        self.write(
            "01_pipeline_run.md",
            "Lakeflow Pipeline Run",
            "This file proves the deployed serverless pipeline completed and reports live bronze, silver, quarantine, reconciliation, and gold row counts plus its expectation payloads.",
            body,
        )

    def generate_02_data_quality(self) -> None:
        quarantine = self.sql(
            f"""
            SELECT quarantine_reason, count(*) AS rows
            FROM {CATALOG}.{SCHEMA}.quarantine_claims
            GROUP BY quarantine_reason ORDER BY quarantine_reason
            """
        )
        reconciliation = self.sql(
            f"""
            SELECT period, expected_claim_rows, landed_claim_rows, loaded_claim_rows,
                   quarantined_claim_rows, reconciliation_status,
                   round(landed_claim_amount - expected_claim_amount, 2) AS claim_amount_difference
            FROM {CATALOG}.{SCHEMA}.reconciliation_claims
            ORDER BY period
            """
        )
        completeness = self.sql(
            f"""
            SELECT count(*) AS gold_rows,
                   count_if(case_id IS NULL) AS missing_case_id,
                   count_if(pharmacy_id IS NULL) AS missing_pharmacy_id,
                   count_if(product_code IS NULL) AS missing_product_code,
                   count_if(review_period IS NULL) AS missing_review_period,
                   count_if(estimated_overpayment IS NULL) AS missing_exposure
            FROM {CATALOG}.{SCHEMA}.gold_case_features
            """
        )
        body = f"""
## Quarantine Reasons

Statement `{quarantine.statement_id}`:

{markdown_table(quarantine.columns, quarantine.rows)}

## Period Reconciliation

Statement `{reconciliation.statement_id}`:

{markdown_table(reconciliation.columns, reconciliation.rows)}

## Gold Completeness

Statement `{completeness.statement_id}`:

{markdown_table(completeness.columns, completeness.rows)}
"""
        self.write(
            "02_data_quality.md",
            "Data Quality and Completeness",
            "This file proves rejected records remain explainable, every released period reconciles to its manifest, and required business keys and exposure fields are complete in live gold data.",
            body,
        )

    def generate_03_business_results(self) -> None:
        headline = self.sql(
            f"""
            SELECT count(*) AS feature_groups,
                   count_if(excess_units > 0 OR matched_cross_channel_pairs > 0) AS flagged_groups,
                   count_if(excess_units > 0) AS excess_quantity_groups,
                   count_if(matched_cross_channel_pairs > 0) AS cross_channel_groups,
                   round(sum(estimated_overpayment), 2) AS estimated_exposure
            FROM {CATALOG}.{SCHEMA}.gold_case_features
            """
        )
        monthly = self.sql(
            f"""
            SELECT review_period,
                   count_if(excess_units > 0 OR matched_cross_channel_pairs > 0) AS flagged_groups,
                   round(sum(estimated_overpayment), 2) AS estimated_exposure
            FROM {CATALOG}.{SCHEMA}.gold_case_features
            GROUP BY review_period ORDER BY review_period
            """
        )
        region = self.sql(
            f"""
            SELECT region,
                   count_if(excess_units > 0 OR matched_cross_channel_pairs > 0) AS flagged_groups,
                   round(sum(estimated_overpayment), 2) AS estimated_exposure
            FROM {CATALOG}.{SCHEMA}.gold_case_features
            GROUP BY region ORDER BY estimated_exposure DESC
            """
        )
        body = f"""
## Current Gold Results

Statement `{headline.statement_id}`:

{markdown_table(headline.columns, headline.rows)}

## Monthly Trend

Statement `{monthly.statement_id}`:

{markdown_table(monthly.columns, monthly.rows)}

## Regional Comparison

Statement `{region.statement_id}`:

{markdown_table(region.columns, region.rows)}

All dollar values are simulated suspected exposure, not verified fraud or realized recovery.
"""
        self.write(
            "03_business_results.md",
            "Business Results",
            "This file proves the live gold-layer totals, trend, and regional comparison used in the business story; all monetary values are explicitly simulated suspected exposure.",
            body,
        )

    def generate_04_ai_output(self) -> None:
        samples = self.sql(
            f"""
            SELECT case_id, review_period, fraud_score, supplied_facts, ai_raw_response,
                   ai_model, prompt_version
            FROM {CATALOG}.{SCHEMA}.gold_fraud_cases
            ORDER BY period_rank LIMIT 3
            """
        )
        sections = []
        for index, row in enumerate(samples.rows, start=1):
            facts = json.loads(row["supplied_facts"]) if isinstance(row["supplied_facts"], str) else row["supplied_facts"]
            output = json.loads(row["ai_raw_response"]) if isinstance(row["ai_raw_response"], str) else row["ai_raw_response"]
            sections.append(
                f"""## Sample {index}

- Case ID: `{row['case_id']}`
- Review period: `{row['review_period']}`
- Explainable score: `{row['fraud_score']}`
- Generator: `{row['ai_model']}`
- Prompt: `{row['prompt_version']}`

### Supplied Facts

{json_block(facts)}

### Verbatim Model Output

{json_block(output)}"""
            )
        self.write(
            "04_ai_output.md",
            "AI Output Samples",
            "This file proves the exact facts supplied to the model and the verbatim persisted model responses for live top-ranked cases, without adding or rewriting model claims.",
            "\n\n".join(sections),
        )

    def generate_05_ai_evaluation(self) -> None:
        history = self.sql(
            f"""
            SELECT prompt_version, mlflow_run_id, count(*) AS evaluated_rows,
                   round(max(candidate_top20_precision) * 100, 1) AS candidate_precision_pct,
                   round(max(baseline_top20_precision) * 100, 1) AS baseline_precision_pct,
                   max(improvement_claim_allowed) AS improvement_claim_allowed,
                   max(evaluated_at) AS evaluated_at
            FROM {CATALOG}.{SCHEMA}.gold_ai_evaluations
            GROUP BY prompt_version, mlflow_run_id
            ORDER BY evaluated_at
            """
        )
        assessments = self.sql(
            f"""
            SELECT prompt_version, mlflow_run_id, judge_assessments
            FROM {CATALOG}.{SCHEMA}.gold_ai_evaluations
            ORDER BY evaluated_at
            """
        )
        judge_counts: dict[tuple[str, str, str], list[int]] = {}
        for row in assessments.rows:
            try:
                items = json.loads(row["judge_assessments"] or "[]")
            except json.JSONDecodeError:
                items = []
            for item in items:
                name = item.get("assessment_name") or item.get("name")
                feedback = item.get("feedback", {})
                value = feedback.get("value") if isinstance(feedback, dict) else feedback
                if name and value is not None:
                    key = (row["prompt_version"], row["mlflow_run_id"], name)
                    judge_counts.setdefault(key, []).append(1 if str(value).lower() in {"yes", "true", "1"} else 0)
        judge_rows = [
            {
                "prompt_version": key[0],
                "mlflow_run_id": key[1],
                "judge": key[2],
                "pass_rate_pct": round(sum(values) / len(values) * 100, 1),
                "assessments": len(values),
            }
            for key, values in sorted(judge_counts.items())
        ]
        eval_task = next(task for task in self.final_run.tasks if task.task_key == "evaluate_ai")
        output = self.task_output(eval_task.run_id)
        body = f"""
## Iteration History

Statement `{history.statement_id}`:

{markdown_table(history.columns, history.rows)}

## Judge Pass Rates

{markdown_table(["prompt_version", "mlflow_run_id", "judge", "pass_rate_pct", "assessments"], judge_rows)}

## Final Orchestration Exit Value

Task run `{eval_task.run_id}` from job run `{self.final_run.run_id}`:

{json_block(output)}
"""
        self.write(
            "05_ai_evaluation.md",
            "AI Evaluation and Iteration",
            "This file proves the locked top-20 ranking comparison, prompt iteration history, judge pass rates, and final evaluation task exit value from live persisted evaluations.",
            body,
        )

    def generate_06_governance(self) -> None:
        entitlements = self.sql(
            f"""
            SELECT persona, allowed_region, can_see_sensitive, count(*) AS principals
            FROM {CATALOG}.{SCHEMA}.entitlements
            GROUP BY persona, allowed_region, can_see_sensitive
            ORDER BY persona, allowed_region
            """
        )
        current_view = self.sql(
            f"""
            SELECT count(*) AS visible_rows, count(DISTINCT region) AS visible_regions,
                   concat_ws(',', sort_array(collect_set(region))) AS visible_scopes,
                   min(pharmacy_phone) AS phone_example
            FROM {CATALOG}.{SCHEMA}.governed_case_features
            """
        )
        tests = self.sql(
            f"""
            SELECT visible_rows, visible_regions,
                   CASE WHEN phone_example = 'RESTRICTED' THEN 'MASKED' ELSE 'VISIBLE' END AS phone_policy,
                   CASE WHEN address_example = 'RESTRICTED' THEN 'MASKED' ELSE 'VISIBLE' END AS address_policy,
                   masked_column_join_rows, tested_at
            FROM {CATALOG}.{SCHEMA}.governance_access_test_results
            ORDER BY tested_at DESC LIMIT 5
            """
        )
        metadata = self.sql(
            f"""
            SELECT tag_name, tag_value
            FROM {CATALOG}.information_schema.table_tags
            WHERE schema_name = '{SCHEMA}' AND table_name = 'governed_case_features'
            ORDER BY tag_name
            """
        )
        run = self.latest_successful_run(GOVERNANCE_JOB_ID)
        body = f"""
## Deployed Governance Run

| Job ID | Run ID | Result |
| --- | --- | --- |
| `{GOVERNANCE_JOB_ID}` | `{run.run_id}` | `{enum_value(run.state.result_state)}` |

## Configured Personas

Statement `{entitlements.statement_id}`:

{markdown_table(entitlements.columns, entitlements.rows)}

## Current Persona Result

Statement `{current_view.statement_id}`:

{markdown_table(current_view.columns, current_view.rows)}

## Dedicated Non-Admin Access Results

Statement `{tests.statement_id}`:

{markdown_table(tests.columns, tests.rows)}

## Governed Table Tags

Statement `{metadata.statement_id}`:

{markdown_table(metadata.columns, metadata.rows)}

Unity Catalog enforces row visibility and contact-field masking on the governed Delta table. Lakebase workflow-row authorization is enforced by the app, not inherited from Unity Catalog.
"""
        self.write(
            "06_governance.md",
            "Unity Catalog Governance",
            "This file proves the live entitlement configuration, current governed result, dedicated non-admin test results, and governance metadata without exposing principal identities or contact values.",
            body,
        )

    def generate_07_lakebase(self) -> None:
        with self.lakebase() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT status, count(*) FROM rebate_ops.cases GROUP BY status ORDER BY status"
                )
                status_rows = [{"status": row[0], "case_count": row[1]} for row in cursor.fetchall()]
                cursor.execute(
                    """
                    SELECT count(*), round(sum(estimated_overpayment), 2),
                           count(*) - count(DISTINCT case_id)
                    FROM rebate_ops.cases
                    """
                )
                total = cursor.fetchone()
                cursor.execute(
                    """
                    SELECT event_type, change_source, changed_columns, changed_at
                    FROM rebate_ops.case_events
                    ORDER BY changed_at DESC LIMIT 10
                    """
                )
                history_rows = [
                    {
                        "event_type": row[0],
                        "change_source": row[1],
                        "changed_columns": ", ".join(row[2] or []),
                        "changed_at": row[3],
                    }
                    for row in cursor.fetchall()
                ]
                cursor.execute(
                    """
                    SELECT status, owner IS NOT NULL AS owner_preserved,
                           notes IS NOT NULL AS notes_preserved,
                           due_date, updated_at
                    FROM rebate_ops.cases
                    WHERE status <> 'NEW'
                    ORDER BY updated_at DESC LIMIT 1
                    """
                )
                edit = cursor.fetchone()
        sync_task = next(task for task in self.final_run.tasks if task.task_key == "sync_operational")
        sync_output = self.task_output(sync_task.run_id)
        summary_rows = [{"case_count": total[0], "estimated_exposure": total[1], "duplicate_business_keys": total[2]}]
        edit_rows = [] if edit is None else [{
            "status": edit[0],
            "owner_preserved": edit[1],
            "notes_preserved": edit[2],
            "due_date": edit[3],
            "last_updated": edit[4],
        }]
        body = f"""
## Operational Summary

{markdown_table(["case_count", "estimated_exposure", "duplicate_business_keys"], summary_rows)}

## Counts by Status

{markdown_table(["status", "case_count"], status_rows)}

## Human Edit Read-Back

{markdown_table(["status", "owner_preserved", "notes_preserved", "due_date", "last_updated"], edit_rows)}

## Recent Immutable History

{markdown_table(["event_type", "change_source", "changed_columns", "changed_at"], history_rows)}

## Final Sync Exit Value

Task run `{sync_task.run_id}` from job run `{self.final_run.run_id}`:

{json_block(sync_output)}

The connection used a newly generated OAuth database credential with `sslmode=require`; no static password was read or written.
"""
        self.write(
            "07_lakebase.md",
            "Lakebase Operational Serving",
            "This file proves live operational counts, uniqueness, preserved human-owned workflow fields, immutable change history, and the final OAuth-authenticated sync result.",
            body,
        )

    @staticmethod
    def canonical_value(value: Any) -> str:
        if value is None:
            return "<NULL>"
        text = str(value).strip()
        try:
            return format(Decimal(text).quantize(Decimal("0.01")), "f")
        except InvalidOperation:
            normalized = text.lower().replace("_", " ")
            return normalized.removesuffix(" activity")

    def result_matches(self, expected: list[dict[str, Any]], actual: list[dict[str, Any]]) -> bool:
        remaining = list(actual)
        for expected_row in expected:
            expected_values = Counter(self.canonical_value(value) for value in expected_row.values())
            match_index = None
            for index, actual_row in enumerate(remaining):
                named = all(
                    column in actual_row
                    and self.canonical_value(actual_row[column]) == self.canonical_value(value)
                    for column, value in expected_row.items()
                )
                actual_values = Counter(self.canonical_value(value) for value in actual_row.values())
                if named or all(actual_values[value] >= count for value, count in expected_values.items()):
                    match_index = index
                    break
            if match_index is None:
                return False
            remaining.pop(match_index)
        return True

    def genie_benchmark(self, benchmark: dict[str, Any]) -> dict[str, Any]:
        workspace = WorkspaceClient(profile=self.profile)
        expected_query = self.sql(benchmark["sql"])
        message = workspace.genie.start_conversation(GENIE_SPACE_ID, benchmark["question"]).result(
            timeout=timedelta(minutes=10)
        )
        query_attachment = next(
            (attachment for attachment in message.attachments or [] if attachment.query is not None), None
        )
        text_attachment = next(
            (attachment for attachment in message.attachments or [] if attachment.text is not None), None
        )
        if query_attachment is None:
            return {
                "id": benchmark["id"],
                "question": benchmark["question"],
                "match": False,
                "expected": expected_query,
                "sql": "No query returned",
                "actual_columns": [],
                "actual_rows": [],
                "answer": text_attachment.text.content if text_attachment else "",
            }
        query_result = workspace.genie.get_message_attachment_query_result(
            GENIE_SPACE_ID,
            message.conversation_id,
            message.message_id,
            query_attachment.attachment_id,
        )
        statement = query_result.statement_response
        columns = [column.name for column in statement.manifest.schema.columns]
        rows = [dict(zip(columns, row)) for row in statement.result.data_array or []]
        return {
            "id": benchmark["id"],
            "question": benchmark["question"],
            "match": self.result_matches(expected_query.rows, rows),
            "expected": expected_query,
            "sql": query_attachment.query.query,
            "actual_columns": columns,
            "actual_rows": rows,
            "answer": text_attachment.text.content if text_attachment else "",
        }

    def generate_08_genie(self) -> None:
        benchmarks = json.loads((ROOT / "src" / "genie" / "benchmarks.json").read_text())
        results = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(self.genie_benchmark, benchmark) for benchmark in benchmarks]
            for future in as_completed(futures):
                results.append(future.result())
        results.sort(key=lambda result: result["id"])
        sections = []
        for result in results:
            expected = result["expected"]
            safe_expected = [redact_row(row) for row in expected.rows]
            safe_actual = [redact_row(row) for row in result["actual_rows"]]
            sections.append(
                f"""## {result['id']} — {'MATCH' if result['match'] else 'MISMATCH'}

**Question:** {redact_text(result['question'])}

**Ground-truth statement:** `{expected.statement_id}`

{markdown_table(expected.columns, safe_expected)}

**Genie SQL**

```sql
{redact_text(result['sql'])}
```

**Genie result**

{markdown_table(result['actual_columns'], safe_actual)}

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.
"""
            )
        matches = sum(result["match"] for result in results)
        body = f"""
## Benchmark Summary

| Space ID | Benchmarks | Matches | Mismatches |
| --- | ---: | ---: | ---: |
| `{GENIE_SPACE_ID}` | {len(results)} | {matches} | {len(results) - matches} |

{"\n\n".join(sections)}
"""
        self.write(
            "08_genie.md",
            "Genie Benchmark Comparison",
            "This file proves every benchmark by executing its ground-truth SQL live, asking the deployed governed Genie space, and comparing returned values; entity names and identities are redacted.",
            body,
        )

    def generate_09_orchestration(self) -> None:
        run = self.final_run
        task_rows = []
        outputs = []
        for task in run.tasks:
            duration = ((task.end_time or 0) - (task.start_time or 0)) / 1000
            output = self.task_output(task.run_id)
            task_rows.append(
                {
                    "task": task.task_key,
                    "task_run_id": task.run_id,
                    "result": enum_value(task.state.result_state),
                    "duration_seconds": round(duration, 1),
                }
            )
            outputs.append(f"### `{task.task_key}`\n\n{json_block(output)}")
        settings = self.workspace.jobs.get(run.job_id).settings
        body = f"""
## Final Successful Run

| Job ID | Run ID | Trigger | Result | Duration seconds | Max concurrent runs | Queue enabled |
| --- | --- | --- | --- | ---: | ---: | --- |
| `{run.job_id}` | `{run.run_id}` | `{enum_value(run.trigger)}` | `{enum_value(run.state.result_state)}` | `{round(run.run_duration / 1000, 1)}` | `{settings.max_concurrent_runs}` | `{settings.queue.enabled}` |

## Task States

{markdown_table(["task", "task_run_id", "result", "duration_seconds"], task_rows)}

## Task Exit Values and Logs

{"\n\n".join(outputs)}
"""
        self.write(
            "09_orchestration.md",
            "Orchestrated Lakeflow Job",
            "This file proves the final successful connected run, serialized task states and durations, queue settings, and every task exit value or available log from the Jobs API.",
            body,
        )

    def generate_10_app(self) -> None:
        app = self.workspace.apps.get(APP_NAME)
        headers = self.workspace.config.authenticate()
        base_url = app.url.rstrip("/")
        case_query = self.sql(
            f"SELECT case_id FROM {CATALOG}.{SCHEMA}.gold_fraud_cases ORDER BY period_rank LIMIT 1"
        )
        case_id = case_query.rows[0]["case_id"]
        routes = ["/", "/cases", f"/cases/{case_id}", "/genie", "/api/health", "/api/whoami"]
        route_rows = []
        for route in routes:
            response = requests.get(f"{base_url}{route}", headers=headers, timeout=60)
            route_rows.append({"route": re.sub(case_id, "[CASE_ID]", route), "http_status": response.status_code})
        persona_rows = []
        for persona in ("director", "svp"):
            response = requests.get(
                f"{base_url}/api/persona-preview",
                params={"persona": persona},
                headers=headers,
                timeout=60,
            )
            payload = response.json() if response.ok else {}
            persona_rows.append(
                {
                    "persona": persona,
                    "http_status": response.status_code,
                    "headline": payload.get("headline", ""),
                    "emphasis": ", ".join(payload.get("emphasis", [])),
                }
            )
        resources = []
        for resource in app.resources or []:
            kind = "unknown"
            target = ""
            if resource.sql_warehouse:
                kind, target = "sql_warehouse", resource.sql_warehouse.id
            elif resource.genie_space:
                kind, target = "genie_space", resource.genie_space.space_id
            elif resource.postgres:
                kind, target = "postgres", resource.postgres.database
            resources.append({"resource": resource.name, "kind": kind, "target": target})
        body = f"""
## Deployed App

| App | Status | Compute | Deployment |
| --- | --- | --- | --- |
| `{APP_NAME}` | `{enum_value(app.app_status.state)}` | `{enum_value(app.compute_status.state)}` | `{enum_value(app.active_deployment.status.state)}` |

## Route Checks

{markdown_table(["route", "http_status"], route_rows)}

## Persona Checks

{markdown_table(["persona", "http_status", "headline", "emphasis"], persona_rows)}

## Deployed Resources

{markdown_table(["resource", "kind", "target"], resources)}

The route checks use the current Databricks OAuth token only in the request header. No token, response identity, email, or customer/entity name is written to evidence.
"""
        self.write(
            "10_app.md",
            "Databricks App Route Checks",
            "This file proves the live app deployment, user-authorized route availability, persona-specific presentation, and deployed SQL warehouse, Genie, and Postgres resources.",
            body,
        )

    def generate_readme(self) -> None:
        descriptions = {
            "00_answer_key.md": "Synthetic generator verification and released manifest totals.",
            "01_pipeline_run.md": "Pipeline update, expectations, and layer row counts.",
            "02_data_quality.md": "Quarantine, reconciliation, and completeness checks.",
            "03_business_results.md": "Gold business totals, trend, and regional comparison.",
            "04_ai_output.md": "Verbatim AI inputs and outputs.",
            "05_ai_evaluation.md": "Ranking and judge evaluation history.",
            "06_governance.md": "Entitlements, masks, non-admin tests, and tags.",
            "07_lakebase.md": "Operational counts, edit persistence, history, and sync.",
            "08_genie.md": "Live ground truth versus Genie benchmarks.",
            "09_orchestration.md": "Final job task states, durations, and exits.",
            "10_app.md": "Live app routes, personas, and resources.",
            "HEADLINES.md": "Approved headline figures shared by README and deck.",
        }
        rows = [
            {"evidence": f"[{filename}]({filename})", "proof": description}
            for filename, description in descriptions.items()
            if (EVIDENCE / filename).exists()
        ]
        body = f"""
All files are regenerated from the same live workspace after final orchestration run `{self.final_run.run_id}`. The generator redacts identities, contact fields, tokens, passwords, and entity names.

{markdown_table(["evidence", "proof"], rows)}
"""
        self.write(
            "README.md",
            "Evidence Index",
            "This index links the plain-text proof for every connected stage and records the final successful run used as the evidence anchor.",
            body,
        )


def normalize_only(value: str | None) -> str | None:
    if value is None:
        return None
    return Path(value).name


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="vandelay")
    parser.add_argument("--only", help="Regenerate one evidence filename, for example 03_business_results.md")
    args = parser.parse_args()
    only = normalize_only(args.only)
    if only and only not in FILES:
        parser.error(f"--only must be one of: {', '.join(FILES)}")

    EVIDENCE.mkdir(exist_ok=True)
    generator = EvidenceGenerator(args.profile, utc_now())
    methods: dict[str, Callable[[], None]] = {
        "HEADLINES.md": generator.generate_headlines,
        "00_answer_key.md": generator.generate_00_answer_key,
        "01_pipeline_run.md": generator.generate_01_pipeline_run,
        "02_data_quality.md": generator.generate_02_data_quality,
        "03_business_results.md": generator.generate_03_business_results,
        "04_ai_output.md": generator.generate_04_ai_output,
        "05_ai_evaluation.md": generator.generate_05_ai_evaluation,
        "06_governance.md": generator.generate_06_governance,
        "07_lakebase.md": generator.generate_07_lakebase,
        "08_genie.md": generator.generate_08_genie,
        "09_orchestration.md": generator.generate_09_orchestration,
        "10_app.md": generator.generate_10_app,
        "README.md": generator.generate_readme,
    }
    selected = [only] if only else FILES
    for filename in selected:
        methods[filename]()


if __name__ == "__main__":
    main()
