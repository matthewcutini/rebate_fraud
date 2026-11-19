#!/usr/bin/env python3
import json
import time
from pathlib import Path

from databricks.sdk import WorkspaceClient


ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS_PATH = ROOT / "src" / "genie" / "benchmarks.json"
OUTPUT_PATH = ROOT / "src" / "genie" / "ground_truth.json"
WAREHOUSE_ID = "5d942ad88a289cf7"


def wait_for_statement(workspace, response):
    while response.status.state.value in {"PENDING", "RUNNING"}:
        time.sleep(2)
        response = workspace.statement_execution.get_statement(response.statement_id)
    return response


def main():
    workspace = WorkspaceClient(profile="vandelay")
    benchmarks = json.loads(BENCHMARKS_PATH.read_text())
    results = []

    for benchmark in benchmarks:
        response = workspace.statement_execution.execute_statement(
            statement=benchmark["sql"],
            warehouse_id=WAREHOUSE_ID,
            catalog="vandelay",
            schema="rebate_fraud",
            wait_timeout="50s",
        )
        response = wait_for_statement(workspace, response)
        state = response.status.state.value
        if state != "SUCCEEDED":
            raise RuntimeError(f"{benchmark['id']} failed: {response.status.error}")

        columns = [column.name for column in response.manifest.schema.columns]
        rows = [dict(zip(columns, row)) for row in response.result.data_array]
        results.append(
            {
                **benchmark,
                "statement_id": response.statement_id,
                "columns": columns,
                "rows": rows,
            }
        )
        print(json.dumps({"id": benchmark["id"], "rows": len(rows), "statement_id": response.statement_id}))

    OUTPUT_PATH.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({"benchmarks": len(results), "output": str(OUTPUT_PATH)}))


if __name__ == "__main__":
    main()
