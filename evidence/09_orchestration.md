# Lakeflow Job Orchestration Evidence

## Deployed Job

- Profile/workspace: `vandelay` / `https://8259554820748444.4.gcp.databricks.com`
- Job: `453506024885536` (`[dev matt_cutini] dev-rebate-fraud-orchestration`)
- Trigger: manual (`ONE_TIME`); selected because the demo data set is fixed and evidence must not drift after capture.
- Concurrency: `max_concurrent_runs: 1`; queue enabled.
- Compute: serverless `STANDARD`.
- Dependency chain: `refresh_pipeline` -> `refresh_governed_consumption` -> `score_cases` -> `explain_top_cases` -> `evaluate_ai` -> `sync_operational` -> `verify_connected_outputs`.

## Successful Run 1

- Run ID: `180075375586623`
- State: `TERMINATED / SUCCESS`
- Total duration: 871 seconds

| Task | State | Execution | Exit value |
|---|---|---:|---|
| `refresh_pipeline` | SUCCESS | 293 s | N/A (pipeline task) |
| `refresh_governed_consumption` | SUCCESS | 44 s | N/A (nested job) |
| `score_cases` | SUCCESS | 7 s | `{}` |
| `explain_top_cases` | SUCCESS | 17 s | `{}` |
| `evaluate_ai` | SUCCESS | 262 s | 20 rows evaluated; baseline and candidate top-20 precision both 0.65; improvement claim disallowed |
| `sync_operational` | SUCCESS | 17 s | 20 source rows; 20 case rows; 0 inserts; 62 history rows |
| `verify_connected_outputs` | SUCCESS | 37 s | Cross-layer values matched |

## Successful Run 2

- Run ID: `806236758003209`
- State: `TERMINATED / SUCCESS`
- Total duration: 1,248 seconds

| Task | State | Execution | Exit value |
|---|---|---:|---|
| `refresh_pipeline` | SUCCESS | 576 s | N/A (pipeline task) |
| `refresh_governed_consumption` | SUCCESS | 53 s | N/A (nested job) |
| `score_cases` | SUCCESS | 8 s | `{}` |
| `explain_top_cases` | SUCCESS | 18 s | `{}` |
| `evaluate_ai` | SUCCESS | 340 s | 20 rows evaluated; baseline and candidate top-20 precision both 0.65; improvement claim disallowed; MLflow run `f57bfc1793f949c49e33910881103dde` |
| `sync_operational` | SUCCESS | 18 s | 20 source rows; 20 case rows; 0 inserts; 82 history rows |
| `verify_connected_outputs` | SUCCESS | 40 s | Cross-layer values matched |

## Rerun Safety

- The operational table remained at 20 cases on both runs and `inserted_rows` remained 0, so the rerun created no duplicate cases.
- History increased from 62 to 82 because the refreshed machine-owned case values produced one trigger-generated change event for each of the 20 cases; human-owned columns remain outside the conflict update.
- The job queue and single-run concurrency setting prevent overlapping refreshes.

## Cross-System Check

The final verifier returned:

| Surface | Case count | Estimated exposure |
|---|---:|---:|
| Gold priority cases | 20 | $893,017.75 |
| Lakebase operational cases | 20 | $893,017.75 |
| Deployed app Postgres resource | 20 | $893,017.75 |
| Governed gold consumed by Genie | 21,845 | $9,823,195.85 |
| Genie answer | 21,845 | $9,823,195.85 |

- App deployed state: `RUNNING`; active deployment: `SUCCEEDED`; resource database: `projects/rebate-fraud-ops/branches/production/databases/databricks-postgres`.
- Genie generated SQL against only `vandelay.rebate_fraud.governed_case_features` and returned the same case count and exposure as the governed table.
- The app count is verified through its deployed Postgres resource and the same Lakebase query used by its case API. Direct job-to-app HTTP invocation is intentionally not used because the app requires a signed-in user's forwarded access token.

## Corrected Failed Run

- Run `1016946532119613` completed all data, AI, and Lakebase tasks but failed `verify_connected_outputs` with HTTP 401 when the job workload token called the user-authorized app endpoint.
- Resolution: verify the deployed app status, deployment status, configured Postgres database, and Lakebase-backed count through platform APIs; retain interactive route checks with signed-in-user authorization in `evidence/10_app.md`.
