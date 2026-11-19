#!/usr/bin/env python3
import json
import time
from pathlib import Path

from databricks.sdk import WorkspaceClient


ROOT = Path(__file__).resolve().parents[1]
SPACE_PATH = ROOT / "src" / "genie" / "space.json"
WAREHOUSE_ID = "5d942ad88a289cf7"


def main():
    workspace = WorkspaceClient(profile="vandelay")
    space = json.loads(SPACE_PATH.read_text())
    examples = space["instructions"]["example_question_sqls"]

    for example in examples:
        response = workspace.statement_execution.execute_statement(
            statement=example["sql"][0],
            warehouse_id=WAREHOUSE_ID,
            catalog="vandelay",
            schema="rebate_fraud",
            wait_timeout="50s",
        )
        while response.status.state.value in {"PENDING", "RUNNING"}:
            time.sleep(2)
            response = workspace.statement_execution.get_statement(response.statement_id)
        if response.status.state.value != "SUCCEEDED":
            raise RuntimeError(f"Example {example['id']} failed: {response.status.error}")
        print(json.dumps({"id": example["id"], "statement_id": response.statement_id, "status": "SUCCEEDED"}))

    print(json.dumps({"examples_validated": len(examples)}))


if __name__ == "__main__":
    main()
