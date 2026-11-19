#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from databricks.sdk import WorkspaceClient


ROOT = Path(__file__).resolve().parents[1]
APP_NAME = "rebate-ops-matt-cutini"
CASE_ID = "31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64"


def main():
    workspace = WorkspaceClient(profile="vandelay")
    app = workspace.apps.get(APP_NAME)
    base_url = app.url.rstrip("/")
    headers = workspace.config.authenticate()
    route_results = []
    for route in ["/", "/cases", f"/cases/{CASE_ID}", "/genie", "/api/health", "/api/whoami"]:
        response = requests.get(f"{base_url}{route}", headers=headers, timeout=60)
        route_results.append({"route": route, "status": response.status_code})
        response.raise_for_status()

    persona_results = {}
    for persona in ["director", "svp"]:
        response = requests.get(
            f"{base_url}/api/persona-preview",
            params={"persona": persona},
            headers=headers,
            timeout=60,
        )
        response.raise_for_status()
        persona_results[persona] = response.json()

    before_response = requests.get(f"{base_url}/api/cases/{CASE_ID}", headers=headers, timeout=60)
    before_response.raise_for_status()
    before = before_response.json()
    note = f"App acceptance check {datetime.now(timezone.utc).isoformat()}"
    case = before["case"]
    update_response = requests.patch(
        f"{base_url}/api/cases/{CASE_ID}",
        headers={**headers, "content-type": "application/json"},
        json={
            "status": "IN_REVIEW",
            "owner": case.get("owner") or "rebate-operations",
            "priority": case.get("priority") or "HIGH",
            "notes": note,
            "dueDate": str(case["due_date"])[:10] if case.get("due_date") else None,
        },
        timeout=60,
    )
    update_response.raise_for_status()
    after_response = requests.get(f"{base_url}/api/cases/{CASE_ID}", headers=headers, timeout=60)
    after_response.raise_for_status()
    after = after_response.json()
    latest_history = after["history"][0]
    assert after["case"]["notes"] == note
    assert latest_history["change_source"] == "APP"

    lines = [
        "# Databricks App Evidence",
        "",
        f"- **App:** `{APP_NAME}`",
        f"- **URL:** {base_url}",
        "- **Execution identity:** Analytics and Genie use the signed-in user's forwarded token; Lakebase uses the app service principal with app-level row authorization.",
        "",
        "## Route Checks",
        "",
        "| Route | HTTP status |",
        "| --- | ---: |",
        *[f"| `{item['route']}` | {item['status']} |" for item in route_results],
        "",
        "## Persona Comparison",
        "",
        f"- **Director lens:** {persona_results['director']['headline']}; shows {', '.join(persona_results['director']['emphasis'])}.",
        f"- **SVP lens:** {persona_results['svp']['headline']}; shows {', '.join(persona_results['svp']['emphasis'])}.",
        "- Persona lenses change presentation only and never expand the signed-in user's governed data access.",
        "",
        "## Lakebase Edit and History",
        "",
        f"- **Case:** `{CASE_ID}`",
        f"- **Before status:** `{before['case']['status']}`",
        f"- **After status:** `{after['case']['status']}`",
        f"- **Saved note:** {note}",
        f"- **Latest history event:** `{latest_history['event_type']}` from `{latest_history['change_source']}` by `{latest_history['changed_by']}` at `{latest_history['changed_at']}`.",
        f"- **Changed columns:** {', '.join(latest_history['changed_columns'])}.",
        "",
        "## Screen Sources",
        "",
        "- Overview and priority queue: user-authorized SQL warehouse queries over governed gold tables.",
        "- Case workspace: governed gold evidence plus mutable Lakebase workflow and history.",
        "- Ask Genie: governed Genie space with answer, table, and generated SQL shown in the AppKit chat surface.",
    ]
    output = ROOT / "evidence" / "10_app.md"
    output.write_text("\n".join(lines) + "\n")
    print(json.dumps({"routes": route_results, "personas": persona_results, "history": latest_history, "evidence": str(output)}))


if __name__ == "__main__":
    main()
