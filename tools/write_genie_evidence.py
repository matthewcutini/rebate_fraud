#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = ROOT / "src" / "genie" / "benchmark_results.json"
OUTPUT_PATH = ROOT / "evidence" / "08_genie.md"


def markdown_table(columns, rows):
    if not rows:
        return "_No rows returned._"
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [str(row.get(column, "")).replace("|", "\\|").replace("\n", " ") for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def main():
    results = json.loads(RESULTS_PATH.read_text())
    matches = sum(result["match"] for result in results)
    lines = [
        "# Genie Agent Evidence",
        "",
        "## Deployed Space",
        "",
        "- **Title:** Rebate Fraud Executive Analytics",
        "- **Space ID:** `01f1e3b93f4b11e79b2fbfcd74547821`",
        "- **Workspace profile:** `vandelay`",
        "- **Warehouse ID:** `5d942ad88a289cf7`",
        "- **Governed source:** `vandelay.rebate_fraud.governed_case_features`",
        "- **Result:** " + f"{matches}/{len(results)} Conversation API benchmark answers matched the checked SQL results.",
        "- **Comparison:** Expected columns must match by name when possible; otherwise row values are compared independent of harmless aliases, capitalization, and extra explanatory columns. Numbers are compared to two decimals.",
        "",
        "## Benchmark Results",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"### {result['id'].upper()} — {'MATCH' if result['match'] else 'MISMATCH'}",
                "",
                f"**Question:** {result['question']}",
                "",
                "**Ground-truth result**",
                "",
                markdown_table(result["expected_columns"], result["expected_rows"]),
                "",
                "**Genie SQL**",
                "",
                "```sql",
                result["genie_sql"],
                "```",
                "",
                "**Genie result**",
                "",
                markdown_table(result["genie_columns"], result["genie_rows"]),
                "",
                "**Genie answer:** " + (result.get("genie_text") or "_No text response._").replace("\n", " "),
                "",
                f"**Value match:** {'Yes' if result['match'] else 'No'}",
                "",
            ]
        )
    OUTPUT_PATH.write_text("\n".join(lines) + "\n")
    print(json.dumps({"output": str(OUTPUT_PATH), "benchmarks": len(results), "matches": matches}))


if __name__ == "__main__":
    main()
