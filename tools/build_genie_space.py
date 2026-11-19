#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS_PATH = ROOT / "src" / "genie" / "benchmarks.json"
OUTPUT_PATH = ROOT / "src" / "genie" / "space.json"


def item_id(namespace, name):
    return hashlib.md5(f"{namespace}:{name}".encode(), usedforsecurity=False).hexdigest()


def column(column_name, description, synonyms=None, **options):
    config = {"column_name": column_name, "description": [description], **options}
    if synonyms:
        config["synonyms"] = synonyms
    return config


def main():
    benchmarks = json.loads(BENCHMARKS_PATH.read_text())
    column_configs = [
        column("case_id", "Stable identifier for one pharmacy, product, and calendar review-month case record.", ["case number", "case identifier"]),
        column("channel_count", "Number of claim channels represented in the case record."),
        column("claim_count", "Total conformed claim lines contributing to the case record."),
        column("claimed_rebate_amount", "Total rebate amount requested for the case record, in US dollars.", ["requested rebate dollars"]),
        column("claimed_units", "Product units claimed for rebate in the calendar review month.", ["rebate units", "requested units"]),
        column("entity_status", "Latest known synthetic pharmacy operating status, such as ACTIVE or CLOSED.", ["pharmacy status"], enable_format_assistance=True, enable_entity_matching=True),
        column("estimated_overpayment", "Illustrative suspected overpayment exposure in US dollars; this is not verified fraud or a recovered amount.", ["exposure", "suspected exposure", "estimated exposure"]),
        column("excess_units", "Claimed units above supported units, floored at zero.", ["unsupported units", "overclaimed units"]),
        column("has_cross_channel_activity", "True only when governed matching found the same underlying activity across medical and pharmacy channels.", ["cross-channel", "duplicate channel activity"]),
        column("has_multiple_source_identities", "True when more than one source identity was resolved to the canonical pharmacy.", ["aliases", "multiple identities"]),
        column("manufacturer_units", "Product units documented through manufacturer-direct movements."),
        column("matched_cross_channel_pairs", "Count of governed medical/pharmacy claim pairs matched as the same underlying activity."),
        column("medical_claim_count", "Count of conformed medical-channel claim lines."),
        column("pharmacy_address", "Sensitive synthetic pharmacy address governed by a Unity Catalog mask.", exclude=True),
        column("pharmacy_claim_count", "Count of conformed pharmacy-channel claim lines."),
        column("pharmacy_fax", "Sensitive synthetic pharmacy fax governed by a Unity Catalog mask.", exclude=True),
        column("pharmacy_id", "Synthetic canonical pharmacy identifier used to aggregate aliases.", ["canonical pharmacy ID"]),
        column("pharmacy_name", "Synthetic canonical pharmacy name shown to business users.", ["pharmacy", "entity name"], enable_format_assistance=True, enable_entity_matching=True),
        column("pharmacy_phone", "Sensitive synthetic pharmacy phone governed by a Unity Catalog mask.", exclude=True),
        column("product_code", "Synthetic product code associated with the case record.", ["product", "NDC"], enable_format_assistance=True, enable_entity_matching=True),
        column("region", "US business region used by the Unity Catalog row-access policy.", ["business region"], enable_format_assistance=True, enable_entity_matching=True),
        column("review_period", "Calendar review month formatted YYYY-MM.", ["month", "review month"], enable_format_assistance=True, enable_entity_matching=True),
        column("source_identity_count", "Number of source identities resolved to the canonical pharmacy."),
        column("state_code", "Two-letter synthetic US state code for the pharmacy.", ["state"], enable_format_assistance=True, enable_entity_matching=True),
        column("supported_units", "Documented product units supporting rebate eligibility; manufacturer and wholesaler movements combined.", ["purchased units", "documented units"]),
        column("wholesaler_units", "Product units documented through wholesaler movements."),
    ]

    samples = [benchmarks[index]["question"] for index in (0, 2, 5, 7, 14)]
    sample_questions = sorted(
        [{"id": item_id("sample", question), "question": [question]} for question in samples],
        key=lambda item: item["id"],
    )

    examples = [
        (
            "What was estimated exposure by state for October 2026?",
            "SELECT governed_case_features.state_code, round(sum(governed_case_features.estimated_overpayment), 2) AS total_estimated_exposure FROM vandelay.rebate_fraud.governed_case_features AS governed_case_features WHERE governed_case_features.review_period = '2026-10' GROUP BY governed_case_features.state_code ORDER BY total_estimated_exposure DESC, governed_case_features.state_code",
        ),
        (
            "What percent of claimed units were excess units by month?",
            "SELECT governed_case_features.review_period, round(100.0 * sum(governed_case_features.excess_units) / nullif(sum(governed_case_features.claimed_units), 0), 2) AS excess_unit_percent FROM vandelay.rebate_fraud.governed_case_features AS governed_case_features GROUP BY governed_case_features.review_period ORDER BY governed_case_features.review_period",
        ),
        (
            "Which products had the most estimated exposure in the West region?",
            "SELECT governed_case_features.product_code, round(sum(governed_case_features.estimated_overpayment), 2) AS total_estimated_exposure FROM vandelay.rebate_fraud.governed_case_features AS governed_case_features WHERE governed_case_features.region = 'WEST' GROUP BY governed_case_features.product_code ORDER BY total_estimated_exposure DESC, governed_case_features.product_code",
        ),
        (
            "Show the monthly evidence for Aster 0241 Family Pharmacy.",
            "SELECT governed_case_features.review_period, governed_case_features.product_code, governed_case_features.claimed_units, governed_case_features.manufacturer_units, governed_case_features.wholesaler_units, governed_case_features.supported_units, governed_case_features.excess_units, governed_case_features.has_cross_channel_activity, round(governed_case_features.estimated_overpayment, 2) AS estimated_overpayment FROM vandelay.rebate_fraud.governed_case_features AS governed_case_features WHERE governed_case_features.pharmacy_name = 'Aster 0241 Family Pharmacy' ORDER BY governed_case_features.review_period, governed_case_features.product_code",
        ),
        (
            "Assess whether key reconciliation fields are complete.",
            "SELECT count_if(governed_case_features.claimed_units IS NULL) AS missing_claimed_units, count_if(governed_case_features.supported_units IS NULL) AS missing_supported_units, count_if(governed_case_features.excess_units IS NULL) AS missing_excess_units, count_if(governed_case_features.estimated_overpayment IS NULL) AS missing_estimated_exposure FROM vandelay.rebate_fraud.governed_case_features AS governed_case_features",
        ),
    ]
    example_question_sqls = sorted(
        [
            {"id": item_id("example", question), "question": [question], "sql": [sql]}
            for question, sql in examples
        ],
        key=lambda item: item["id"],
    )

    measures = [
        ("suspected_case_count", "Suspected Case Count", "COUNT(DISTINCT governed_case_features.case_id)", ["case count"]),
        ("total_estimated_exposure", "Total Estimated Exposure", "SUM(governed_case_features.estimated_overpayment)", ["exposure", "suspected exposure"]),
        ("total_excess_units", "Total Excess Units", "SUM(governed_case_features.excess_units)", ["unsupported units"]),
    ]
    filters = [
        ("cross_channel_cases", "Cross-channel Cases", "governed_case_features.has_cross_channel_activity = true", ["cross-channel"]),
        ("excess_claim_cases", "Excess Claim Cases", "governed_case_features.claimed_units > governed_case_features.supported_units", ["overclaimed", "unsupported claims"]),
        ("multiple_identity_cases", "Multiple Identity Cases", "governed_case_features.has_multiple_source_identities = true", ["aliases", "multiple identities"]),
    ]

    benchmark_questions = sorted(
        [
            {
                "id": item_id("benchmark", benchmark["id"]),
                "question": [benchmark["question"]],
                "answer": [{"format": "SQL", "content": [benchmark["sql"]]}],
            }
            for benchmark in benchmarks
        ],
        key=lambda item: item["id"],
    )

    text = """## PURPOSE
- Answer governed rebate-fraud exposure and reconciliation questions for the Director of Rebate Operations and SVP of Contracting and Rebates.

## DISAMBIGUATION
- Treat month and review month as calendar review_period values; never invent missing months.
- Treat case as one case_id at the pharmacy, product, and review-month grain.

## DATA QUALITY NOTES
- Return only review periods present in governed_case_features and state the date range when summarizing trends.

## CONSTRAINTS
- Do not describe suspected exposure as verified fraud, recovered dollars, payment denial, or legal outcome.
- Do not answer questions about investigator status, ownership, communications, recoveries, or escalation because those fields are not in this source.
- Do not expose pharmacy_address, pharmacy_phone, or pharmacy_fax.

## Instructions you must follow when providing summaries
- Present monetary exposure in US dollars rounded to two decimals and unit quantities as units.
- Rank highest or top results by descending estimated_overpayment unless the user names another measure; break ties with stable identifiers."""

    payload = {
        "version": 2,
        "config": {"sample_questions": sample_questions},
        "data_sources": {
            "tables": [
                {
                    "identifier": "vandelay.rebate_fraud.governed_case_features",
                    "column_configs": sorted(column_configs, key=lambda item: item["column_name"]),
                }
            ]
        },
        "instructions": {
            "example_question_sqls": example_question_sqls,
            "sql_snippets": {
                "expressions": [],
                "filters": sorted(
                    [
                        {
                            "id": item_id("filter", alias),
                            "display_name": display_name,
                            "sql": [sql],
                            "synonyms": synonyms,
                        }
                        for alias, display_name, sql, synonyms in filters
                    ],
                    key=lambda item: item["id"],
                ),
                "measures": sorted(
                    [
                        {
                            "id": item_id("measure", alias),
                            "alias": alias,
                            "display_name": display_name,
                            "sql": [sql],
                            "synonyms": synonyms,
                        }
                        for alias, display_name, sql, synonyms in measures
                    ],
                    key=lambda item: item["id"],
                ),
            },
            "text_instructions": [{"id": item_id("text", "instructions"), "content": [text]}],
        },
        "benchmarks": {"questions": benchmark_questions},
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"output": str(OUTPUT_PATH), "benchmarks": len(benchmark_questions)}))


if __name__ == "__main__":
    main()
