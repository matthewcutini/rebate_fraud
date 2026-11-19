#!/usr/bin/env python3
import json
from pathlib import Path

from databricks.sdk import WorkspaceClient


ROOT = Path(__file__).resolve().parents[1]
SPACE_PATH = ROOT / "src" / "genie" / "space.json"
METADATA_PATH = ROOT / "src" / "genie" / "space_metadata.json"
WAREHOUSE_ID = "5d942ad88a289cf7"
TITLE = "Rebate Fraud Executive Analytics"
DESCRIPTION = "Governed analysis of synthetic rebate-fraud exposure, reconciliation evidence, channel overlap, and pharmacy identity signals for rebate operations leaders."
PARENT_PATH = "/Workspace/Users/matt.cutini@databricks.com/genie_spaces"


def main():
    workspace = WorkspaceClient(profile="vandelay")
    serialized_space = SPACE_PATH.read_text().strip()
    existing = next((space for space in workspace.genie.list_spaces().spaces or [] if space.title == TITLE), None)

    if existing:
        deployed = workspace.genie.update_space(
            existing.space_id,
            warehouse_id=WAREHOUSE_ID,
            title=TITLE,
            description=DESCRIPTION,
            parent_path=PARENT_PATH,
            serialized_space=serialized_space,
        )
        operation = "updated"
    else:
        deployed = workspace.genie.create_space(
            warehouse_id=WAREHOUSE_ID,
            title=TITLE,
            description=DESCRIPTION,
            parent_path=PARENT_PATH,
            serialized_space=serialized_space,
        )
        operation = "created"

    read_back = workspace.genie.get_space(deployed.space_id, include_serialized_space=True)
    SPACE_PATH.write_text(json.dumps(json.loads(read_back.serialized_space), indent=2) + "\n")
    metadata = {
        "space_id": read_back.space_id,
        "title": read_back.title,
        "description": read_back.description,
        "warehouse_id": read_back.warehouse_id,
        "parent_path": read_back.parent_path,
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps({"operation": operation, **metadata}))


if __name__ == "__main__":
    main()
