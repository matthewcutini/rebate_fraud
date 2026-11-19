# Databricks notebook source
import json
import shutil
from pathlib import Path


def widget(name: str, default: str) -> str:
    try:
        return dbutils.widgets.get(name)  # type: ignore[name-defined]
    except Exception:
        return default


catalog = widget("catalog", "vandelay")
schema = widget("schema", "rebate_fraud")
volume = widget("volume", "landing")
period = widget("period", "2026-10")
root = Path(f"/Volumes/{catalog}/{schema}/{volume}")
source = root / "holdback" / period
target = root / "ready" / period

if not source.exists():
    raise FileNotFoundError(f"Held-out period does not exist: {source}")

if target.exists():
    shutil.rmtree(target)
shutil.copytree(source, target)

summary = {
    "period": period,
    "source": str(source),
    "target": str(target),
    "files": sum(1 for path in target.rglob("*") if path.is_file()),
    "remaining_holdback_periods": sorted(path.name for path in (root / "holdback").iterdir() if path.name != period),
}
print(json.dumps(summary, sort_keys=True))
try:
    dbutils.notebook.exit(json.dumps(summary, sort_keys=True))  # type: ignore[name-defined]
except NameError:
    pass
