Generated 2026-11-19T20:31:50Z by tools/generate_evidence.py from the live workspace

# AI Evaluation and Iteration

This file proves the locked top-20 ranking comparison, prompt iteration history, judge pass rates, and final evaluation task exit value from live persisted evaluations.

## Iteration History

Statement `01f1e458-4091-15f5-a9a2-8aac1f2fdb25`:

| prompt_version | mlflow_run_id | evaluated_rows | candidate_precision_pct | baseline_precision_pct | improvement_claim_allowed | evaluated_at |
| --- | --- | --- | --- | --- | --- | --- |
| prompt-v1 | b49e33da3b45442a9827e5f4750c7f93 | 20 | 0.0 | 0.0 | false | 2026-11-19T00:08:13.271Z |
| prompt-v1 | fe80568d98a94035a139282f13562968 | 20 | 65.0 | 65.0 | false | 2026-11-19T00:22:18.737Z |
| prompt-v2 | c683dcf24bf549cdb372d84a54c0d831 | 20 | 65.0 | 65.0 | false | 2026-11-19T00:30:11.650Z |
| prompt-v2 | 38a5d1115673471aba4505498678ceb8 | 20 | 65.0 | 65.0 | false | 2026-11-19T19:00:33.868Z |
| prompt-v2 | ab0f7182d98b4e71ab12190c252f8364 | 20 | 65.0 | 65.0 | false | 2026-11-19T19:18:17.204Z |
| prompt-v2 | f57bfc1793f949c49e33910881103dde | 20 | 65.0 | 65.0 | false | 2026-11-19T19:44:13.760Z |

## Judge Pass Rates

| prompt_version | mlflow_run_id | judge | pass_rate_pct | assessments |
| --- | --- | --- | --- | --- |
| prompt-v1 | b49e33da3b45442a9827e5f4750c7f93 | actionable_next_step | 90.0 | 20 |
| prompt-v1 | b49e33da3b45442a9827e5f4750c7f93 | grounded_in_supplied_facts | 30.0 | 20 |
| prompt-v1 | b49e33da3b45442a9827e5f4750c7f93 | neutral_investigative_language | 100.0 | 20 |
| prompt-v1 | b49e33da3b45442a9827e5f4750c7f93 | no_invented_data | 30.0 | 20 |
| prompt-v1 | fe80568d98a94035a139282f13562968 | actionable_next_step | 95.0 | 20 |
| prompt-v1 | fe80568d98a94035a139282f13562968 | grounded_in_supplied_facts | 35.0 | 20 |
| prompt-v1 | fe80568d98a94035a139282f13562968 | neutral_investigative_language | 100.0 | 20 |
| prompt-v1 | fe80568d98a94035a139282f13562968 | no_invented_data | 45.0 | 20 |
| prompt-v2 | 38a5d1115673471aba4505498678ceb8 | actionable_next_step | 100.0 | 20 |
| prompt-v2 | 38a5d1115673471aba4505498678ceb8 | grounded_in_supplied_facts | 45.0 | 20 |
| prompt-v2 | 38a5d1115673471aba4505498678ceb8 | neutral_investigative_language | 100.0 | 20 |
| prompt-v2 | 38a5d1115673471aba4505498678ceb8 | no_invented_data | 35.0 | 20 |
| prompt-v2 | ab0f7182d98b4e71ab12190c252f8364 | actionable_next_step | 100.0 | 20 |
| prompt-v2 | ab0f7182d98b4e71ab12190c252f8364 | grounded_in_supplied_facts | 40.0 | 20 |
| prompt-v2 | ab0f7182d98b4e71ab12190c252f8364 | neutral_investigative_language | 100.0 | 20 |
| prompt-v2 | ab0f7182d98b4e71ab12190c252f8364 | no_invented_data | 25.0 | 20 |
| prompt-v2 | c683dcf24bf549cdb372d84a54c0d831 | actionable_next_step | 100.0 | 20 |
| prompt-v2 | c683dcf24bf549cdb372d84a54c0d831 | grounded_in_supplied_facts | 35.0 | 20 |
| prompt-v2 | c683dcf24bf549cdb372d84a54c0d831 | neutral_investigative_language | 100.0 | 20 |
| prompt-v2 | c683dcf24bf549cdb372d84a54c0d831 | no_invented_data | 25.0 | 20 |
| prompt-v2 | f57bfc1793f949c49e33910881103dde | actionable_next_step | 100.0 | 20 |
| prompt-v2 | f57bfc1793f949c49e33910881103dde | grounded_in_supplied_facts | 40.0 | 20 |
| prompt-v2 | f57bfc1793f949c49e33910881103dde | neutral_investigative_language | 100.0 | 20 |
| prompt-v2 | f57bfc1793f949c49e33910881103dde | no_invented_data | 35.0 | 20 |

## Final Orchestration Exit Value

Task run `119335936168131` from job run `806236758003209`:

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
