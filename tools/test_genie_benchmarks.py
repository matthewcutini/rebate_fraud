#!/usr/bin/env python3
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

from databricks.sdk import WorkspaceClient


ROOT = Path(__file__).resolve().parents[1]
GROUND_TRUTH_PATH = ROOT / "src" / "genie" / "ground_truth.json"
METADATA_PATH = ROOT / "src" / "genie" / "space_metadata.json"
OUTPUT_PATH = ROOT / "src" / "genie" / "benchmark_results.json"


def canonical_value(value):
    if value is None:
        return "<NULL>"
    text = str(value).strip()
    try:
        number = Decimal(text).quantize(Decimal("0.01"))
        return format(number, "f")
    except InvalidOperation:
        return text.lower()


def row_values_match(expected, actual):
    expected_values = Counter(canonical_value(value) for value in expected.values())
    actual_values = Counter(canonical_value(value) for value in actual.values())
    return all(actual_values[value] >= count for value, count in expected_values.items())


def expected_rows_match(expected_rows, actual_rows):
    remaining = list(actual_rows)
    for expected in expected_rows:
        match_index = next(
            (
                index
                for index, actual in enumerate(remaining)
                if all(
                    column in actual and canonical_value(actual[column]) == canonical_value(value)
                    for column, value in expected.items()
                ) or row_values_match(expected, actual)
            ),
            None,
        )
        if match_index is None:
            return False
        remaining.pop(match_index)
    return True


def run_benchmark(space_id, benchmark):
    workspace = WorkspaceClient(profile="vandelay")
    message = workspace.genie.start_conversation(space_id, benchmark["question"]).result(
        timeout=timedelta(minutes=10)
    )
    message_dict = message.as_dict()
    query_attachment = next(
        (attachment for attachment in message.attachments or [] if attachment.query is not None),
        None,
    )
    text_attachment = next(
        (attachment for attachment in message.attachments or [] if attachment.text is not None),
        None,
    )

    if query_attachment is None:
        return {
            "id": benchmark["id"],
            "question": benchmark["question"],
            "status": message.status.value,
            "match": False,
            "reason": "No query attachment returned",
            "genie_text": text_attachment.text.content if text_attachment else None,
            "message": message_dict,
        }

    query_result = workspace.genie.get_message_attachment_query_result(
        space_id,
        message.conversation_id,
        message.message_id,
        query_attachment.attachment_id,
    )
    statement_response = query_result.statement_response
    actual_columns = [column.name for column in statement_response.manifest.schema.columns]
    actual_data = statement_response.result.data_array or []
    actual_rows = [dict(zip(actual_columns, row)) for row in actual_data]
    values_match = expected_rows_match(benchmark["rows"], actual_rows)

    return {
        "id": benchmark["id"],
        "question": benchmark["question"],
        "status": message.status.value,
        "match": values_match,
        "expected_columns": benchmark["columns"],
        "expected_rows": benchmark["rows"],
        "genie_sql": query_attachment.query.query,
        "genie_columns": actual_columns,
        "genie_rows": actual_rows,
        "genie_text": text_attachment.text.content if text_attachment else None,
        "conversation_id": message.conversation_id,
        "message_id": message.message_id,
        "attachment_id": query_attachment.attachment_id,
    }


def main():
    ground_truth = json.loads(GROUND_TRUTH_PATH.read_text())
    space_id = json.loads(METADATA_PATH.read_text())["space_id"]
    results = []

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_benchmark, space_id, benchmark): benchmark["id"]
            for benchmark in ground_truth
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps({"id": result["id"], "match": result["match"], "status": result["status"]}))

    results.sort(key=lambda item: item["id"])
    OUTPUT_PATH.write_text(json.dumps(results, indent=2) + "\n")
    matches = sum(result["match"] for result in results)
    print(json.dumps({"benchmarks": len(results), "matches": matches, "mismatches": len(results) - matches}))


if __name__ == "__main__":
    main()
