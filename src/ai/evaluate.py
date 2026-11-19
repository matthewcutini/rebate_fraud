# Databricks notebook source
import json
import os
from datetime import datetime, timezone

import mlflow
from mlflow.genai.scorers import Guidelines


def widget(name: str, default: str) -> str:
    try:
        dbutils.widgets.text(name, default)  # type: ignore[name-defined]
        return dbutils.widgets.get(name)  # type: ignore[name-defined]
    except NameError:
        return default


catalog = widget("catalog", "vandelay")
schema = widget("schema", "rebate_fraud")
judge_model = widget("judge_model", "databricks-claude-haiku-4-5")
prompt_version = widget("prompt_version", "prompt-v1")
held_out_period = "2026-10"
judge_uri = f"databricks:/{judge_model}"
os.environ["MLFLOW_GENAI_EVAL_MAX_WORKERS"] = "2"

cases = spark.table(f"{catalog}.{schema}.gold_fraud_cases").orderBy("period_rank").collect()  # type: ignore[name-defined]
if len(cases) != 20:
    raise ValueError(f"Expected 20 held-out AI cases, found {len(cases)}")

evaluation_data = []
for case in cases:
    evaluation_data.append(
        {
            "inputs": {
                "case_id": case.case_id,
                "supplied_facts": case.supplied_facts,
                "task": "Explain the supplied rebate case and recommend one investigative next action.",
            },
            "outputs": {
                "response": case.ai_raw_response,
            },
        }
    )

scorers = [
    Guidelines(
        name="grounded_in_supplied_facts",
        guidelines="Every factual assertion in the response must be directly supported by the supplied_facts in the request. Likely possibilities must not be presented as facts.",
        model=judge_uri,
    ),
    Guidelines(
        name="actionable_next_step",
        guidelines="The response must recommend a concrete, proportionate investigation action based only on the supplied facts.",
        model=judge_uri,
    ),
    Guidelines(
        name="no_invented_data",
        guidelines="The response must not invent a person, organization, amount, date, document, contact detail, claim, or event absent from supplied_facts.",
        model=judge_uri,
    ),
    Guidelines(
        name="neutral_investigative_language",
        guidelines="The response must remain neutral, describe indicators rather than guilt, and must not state or imply that fraud is proven.",
        model=judge_uri,
    ),
]

mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Users/matt.cutini@databricks.com/rebate-fraud-ai-evaluation")
with mlflow.start_run(run_name=prompt_version):
    result = mlflow.genai.evaluate(data=evaluation_data, scorers=scorers)


products = ("99999-0101-01", "99999-0102-01", "99999-0201-01", "99999-0301-01")
truth_keys = set()
period_index = 11
for local_index in range(7):
    case_index = period_index * 7 + local_index
    truth_keys.add((f"REF-{(17 * case_index + 11) % 500 + 1:06d}", products[case_index % len(products)]))
for local_index in range(4):
    case_index = period_index * 4 + local_index
    truth_keys.add((f"REF-{(19 * case_index + 101) % 500 + 1:06d}", products[(case_index + 1) % len(products)]))
for local_index in range(2):
    case_index = period_index * 2 + local_index
    truth_keys.add((f"REF-{(23 * case_index + 211) % 500 + 1:06d}", products[(case_index + 2) % len(products)]))

scored = spark.table(f"{catalog}.{schema}.gold_fraud_case_scores").filter(f"review_period = '{held_out_period}'").collect()  # type: ignore[name-defined]
candidate_ranked = sorted(scored, key=lambda row: (-row.fraud_score, -float(row.estimated_overpayment), row.case_id))
baseline_ranked = sorted(
    scored,
    key=lambda row: (
        -(1 if row.excess_units > 0 or row.matched_cross_channel_pairs > 0 else 0),
        -float(row.estimated_overpayment),
        row.case_id,
    ),
)


def precision_at_20(rows):
    return sum((row.pharmacy_id, row.product_code) in truth_keys for row in rows[:20]) / 20.0


candidate_precision = precision_at_20(candidate_ranked)
baseline_precision = precision_at_20(baseline_ranked)
claim_allowed = candidate_precision >= baseline_precision + 0.10

traces = mlflow.search_traces(run_id=result.run_id)
trace_by_case = {}
for _, trace in traces.iterrows():
    request = trace.get("request", {})
    if isinstance(request, str):
        try:
            request = json.loads(request)
        except json.JSONDecodeError:
            request = {}
    case_id = request.get("case_id") or request.get("inputs", {}).get("case_id")
    if case_id:
        trace_by_case[case_id] = trace

rows = []
for case in cases:
    trace = trace_by_case.get(case.case_id)
    assessments = [] if trace is None else trace.get("assessments", [])
    assessment_json = json.dumps(assessments, default=str, sort_keys=True)
    rows.append(
        {
            "case_id": case.case_id,
            "review_period": held_out_period,
            "prompt_version": prompt_version,
            "generator_model": case.ai_model,
            "judge_model": judge_model,
            "mlflow_run_id": result.run_id,
            "supplied_facts": case.supplied_facts,
            "ai_output": case.ai_raw_response,
            "judge_assessments": assessment_json,
            "is_planted_fraud": (case.pharmacy_id, case.product_code) in truth_keys,
            "candidate_top20_precision": candidate_precision,
            "baseline_top20_precision": baseline_precision,
            "improvement_claim_allowed": claim_allowed,
            "evaluated_at": datetime.now(timezone.utc),
        }
    )

output = spark.createDataFrame(rows)  # type: ignore[name-defined]
output.write.mode("append").option("mergeSchema", "true").saveAsTable(f"{catalog}.{schema}.gold_ai_evaluations")

summary = {
    "prompt_version": prompt_version,
    "mlflow_run_id": result.run_id,
    "evaluated_rows": len(rows),
    "candidate_top20_precision": candidate_precision,
    "baseline_top20_precision": baseline_precision,
    "improvement_claim_allowed": claim_allowed,
    "judge_metrics": result.metrics,
}
print(json.dumps(summary, default=str, sort_keys=True))
dbutils.notebook.exit(json.dumps(summary, default=str, sort_keys=True))  # type: ignore[name-defined]
