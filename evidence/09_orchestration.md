Generated 2026-11-19T20:32:57Z by tools/generate_evidence.py from the live workspace

# Orchestrated Lakeflow Job

This file proves the final successful connected run, serialized task states and durations, queue settings, and every task exit value or available log from the Jobs API.

## Final Successful Run

| Job ID | Run ID | Trigger | Result | Duration seconds | Max concurrent runs | Queue enabled |
| --- | --- | --- | --- | ---: | ---: | --- |
| `453506024885536` | `806236758003209` | `ONE_TIME` | `SUCCESS` | `1248.2` | `1` | `True` |

## Task States

| task | task_run_id | result | duration_seconds |
| --- | --- | --- | --- |
| sync_operational | 561038139248061 | SUCCESS | 20.3 |
| refresh_governed_consumption | 473794132839922 | SUCCESS | 54.1 |
| evaluate_ai | 119335936168131 | SUCCESS | 525.9 |
| verify_connected_outputs | 1027581777514410 | SUCCESS | 42.2 |
| score_cases | 978626615224898 | SUCCESS | 8.4 |
| refresh_pipeline | 374240154551089 | SUCCESS | 576.5 |
| explain_top_cases | 947391055438722 | SUCCESS | 18.9 |

## Task Exit Values and Logs

### `sync_operational`

```json
{
  "notebook_result": {
    "case_rows": 20,
    "endpoint": "projects/rebate-fraud-ops/branches/production/endpoints/primary",
    "history_rows": 82,
    "inserted_rows": 0,
    "source_rows": 20
  }
}
```

### `refresh_governed_consumption`

```json
{
  "result": "No task exit value returned by the Jobs API."
}
```

### `evaluate_ai`

```json
{
  "notebook_result": {
    "baseline_top20_precision": 0.65,
    "candidate_top20_precision": 0.65,
    "evaluated_rows": 20,
    "improvement_claim_allowed": false,
    "judge_metrics": {
      "actionable_next_step/mean": 1.0,
      "grounded_in_supplied_facts/mean": 0.4,
      "neutral_investigative_language/mean": 1.0,
      "no_invented_data/mean": 0.35
    },
    "mlflow_run_id": "f57bfc1793f949c49e33910881103dde",
    "prompt_version": "prompt-v2"
  }
}
```

### `verify_connected_outputs`

```json
{
  "notebook_result": {
    "app": {
      "case_count": 20,
      "database": "projects/rebate-fraud-ops/branches/production/databases/databricks-postgres",
      "deployment_status": "SUCCEEDED",
      "status": "RUNNING"
    },
    "genie": {
      "case_count": 21845,
      "exposure": "9823195.85"
    },
    "genie_sql": "SELECT COUNT(DISTINCT `case_id`) AS `suspected_case_count`, ROUND(SUM(`estimated_overpayment`), 2) AS `total_estimated_exposure` FROM `vandelay`.`rebate_fraud`.`governed_case_features`",
    "gold_priority": {
      "case_count": 20,
      "exposure": "893017.75"
    },
    "governed_gold": {
      "case_count": 21845,
      "exposure": "9823195.85"
    },
    "lakebase": {
      "case_count": 20,
      "exposure": "893017.75"
    }
  }
}
```

### `score_cases`

```json
{
  "sql_output": {}
}
```

### `refresh_pipeline`

```json
{
  "result": "No task exit value returned by the Jobs API."
}
```

### `explain_top_cases`

```json
{
  "sql_output": {}
}
```
