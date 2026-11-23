# Rebate Fraud Prevention for a Glucose Monitor Manufacturer

**In this demo, we surface $9,823,195.85 in simulated suspected rebate overpayment exposure for investigation.**

## Who It Is For

This prototype is for a glucose monitor manufacturer in Life Sciences/MedTech. It serves the Director of Rebate Operations, who runs investigations, and the SVP of Contracting, Rebates, who owns the financial and control outcome.

All organizations, claims, pharmacies, identities, transactions, communications, and outcomes are synthetic and vendor-neutral. The approved coverage headline is 110,000 released synthetic claims across 11 released periods. See [`evidence/HEADLINES.md`](evidence/HEADLINES.md).

## The Business Problem and Why Now

- The manufacturer receives data on rebate requests from many different sources in different formats, making it hard to reconcile the amounts of glucose-monitor product each pharmacy actually purchased with how many rebates they are requesting.
- Rebate requests can come through medical and pharmacy channels, while aliases and changing identifiers make one pharmacy look like several businesses.
- Analysts must manually combine manufacturer sales, wholesaler distribution, rebate claims, and pharmacy reference data before they can decide which cases deserve attention because they are suspected fraud.
- Outreach, responses, decisions, and legal escalation evidence are fragmented, weakening the paper trail required for recovery and audit.
- Growth, gross-to-net pressure, and the risk of a pharmacy closing make earlier detection and action more urgent.

## What It Delivers

| Outcome for the customer | How it shows up | Proof |
|---|---|---|
| One reconciled view of claims, purchases, distribution, and pharmacy identities. | Lakeflow ingests raw files, conforms both claim channels, quarantines unusable records, and reconciles each released period. | [`evidence/01_pipeline_run.md`](evidence/01_pipeline_run.md), [`evidence/02_data_quality.md`](evidence/02_data_quality.md) |
| Governed access to investigation evidence without exposing restricted contact fields. | Unity Catalog row filters, masks, tags, entitlements, and non-admin access tests protect the governed gold table. | [`evidence/06_governance.md`](evidence/06_governance.md) |
| An explainable priority list instead of a messy list based on gut feelings. | Named score components rank cases; generated explanations and next actions remain subject to human review. | [`evidence/04_ai_output.md`](evidence/04_ai_output.md), [`evidence/05_ai_evaluation.md`](evidence/05_ai_evaluation.md) |
| A durable operational paper trail that preserves the history of the teams' efforts to work with pharmacies suspected of fraud. | Lakebase preserves status, owner, notes, due date, and immutable case history while machine-owned fields refresh. | [`evidence/07_lakebase.md`](evidence/07_lakebase.md) |
| Governed self-service answers for rebate leaders. | Genie answers benchmarked questions using only the governed consumption table. | [`evidence/08_genie.md`](evidence/08_genie.md) |
| One app for the whole team to review evidence, manage cases, and ask governed questions. | The Databricks App presents operations, priority cases, case actions, history, and Genie with user-aware authorization. | [`evidence/10_app.md`](evidence/10_app.md) |
| An end-to-end solution with the flexibility to evolve. | One queued Lakeflow Job runs the pipeline, governance refresh, scoring, AI evaluation, Lakebase sync, and cross-system verification in dependency order. | [`evidence/09_orchestration.md`](evidence/09_orchestration.md) |

## Value: Fraud Prevention

| Value driver | From the data | Illustrative value | Assumptions and limits |
|---|---|---|---|
| Investigation coverage | 110,000 released synthetic claims across 11 released periods. | A repeatable evidence base for finding and prioritizing suspected rebate leakage. | Measured from live control manifests over simulated data; it does not represent production claim volume. |
| Suspected overpayment exposure | $9,823,195.85 across the live gold feature population. | The exposure pool available for investigation prioritization. | Simulated suspected exposure; it is not verified fraud, prevented loss, recovered cash, or guaranteed value. |
| Fraud prevention and recovery | No verified recovery outcome exists in the synthetic prototype. | Not yet verified. | No recovery rate, prevention rate, avoided-loss multiplier, or labor-savings assumption is applied until a real baseline and adjudicated outcomes exist. |

The exact approved wording, denominator, measurement time, classification, and evidence source for both headline figures are recorded in [`evidence/HEADLINES.md`](evidence/HEADLINES.md).

## How It Works

Raw rebate data becomes governed investigation evidence, explainable case priorities, mutable operational records, executive answers, and human case actions through one connected Databricks journey.

| Stage | What it does | Implementation |
|---|---|---|
| Lakeflow | Loads raw files with Auto Loader, conforms channels, applies expectations, quarantines defects, reconciles manifests, resolves identities, and creates gold features. | [`resources/pipeline.yml`](resources/pipeline.yml), [`src/pipeline/`](src/pipeline/), [`src/data/`](src/data/) |
| Unity Catalog | Publishes the governed consumption table with row filtering, sensitive-field masks, tags, comments, entitlements, and least-privilege tests. | [`resources/governance.job.yml`](resources/governance.job.yml), [`src/governance/`](src/governance/) |
| Intelligent step | Applies deterministic score components, generates structured explanations for prioritized cases, and persists MLflow judge results. | [`resources/ai.job.yml`](resources/ai.job.yml), [`src/ai/`](src/ai/) |
| Lakebase | Upserts machine-owned case fields while preserving human-owned workflow fields and database-triggered history. | [`resources/lakebase_sync.job.yml`](resources/lakebase_sync.job.yml), [`src/serve/upsert_lakebase.py`](src/serve/upsert_lakebase.py) |
| Genie | Defines a reproducible governed space, business instructions, examples, benchmarks, and live answer comparisons. | [`src/genie/`](src/genie/), [`tools/test_genie_benchmarks.py`](tools/test_genie_benchmarks.py) |
| Databricks App | Combines governed analytics, case workflow, history, persona lenses, and Genie using mixed execution identity. | [`resources/rebate_fraud.app.yml`](resources/rebate_fraud.app.yml), [`src/app/`](src/app/) |

The complete dependency graph and connected verification task are defined in [`resources/job.yml`](resources/job.yml).

## Decisions and Trade-offs

1. We chose an end-to-end rebate investigation workflow over a narrow duplicate detector because fraud prevention requires detection, action, and a complete paper trail.
2. We chose a hybrid of entity resolution, explainable scoring, and grounded generation over a black-box classifier because synthetic labels cannot justify automated fraud decisions.
3. We chose raw files in a Unity Catalog volume with Auto Loader over direct table generation because visible ingestion, late files, and replayable source evidence matter to the story.
4. We chose severity-based data quality over warning on every defect because untraceable records must be quarantined while correctable issues can remain observable.
5. We chose a separate governed consumption table with row filters and masks over exposing ungoverned gold because application and Genie consumers must inherit a testable access boundary.
6. We chose a Lakebase upsert that updates only machine-owned fields over a read-only synced table because investigators need mutable workflow state that survives analytical refreshes.
7. We chose user authorization for warehouse and Genie requests, with the app service principal for Lakebase, over one service principal for everything because Unity Catalog policies must apply to the signed-in viewer.
8. We chose one governed Genie source over several overlapping tables because a single business grain reduces ambiguity and preserves masks and row filters.
9. We chose an operational investigation console over a dashboard because the primary outcome is taking and recording action on a case.
10. We chose a manually triggered, queued orchestration job over file arrival because evaluator evidence must remain deterministic after capture.

## How AI Tools Were Used

The build used Genie CLI as the coding agent, Databricks CLI and Declarative Automation Bundles for deployment, the Databricks Python SDK for workspace automation, SQL Statement Execution for live proof, and product-specific Databricks skills for bundles, jobs, pipelines, SQL, Unity Catalog, Lakebase, Genie, Apps, app design, and MLflow evaluation.

The workflow kept AI useful without treating its first answer as truth: frame and approve the business decision, inspect the live workspace, make one focused change, deploy it, read the deployed object back, run it, compare results with deterministic SQL, record failures, and regenerate evaluator-readable evidence from live APIs.

The practices that constrained AI output were deterministic synthetic data, a locked temporal evaluation protocol, explainable score components, a different-family judge, parameterized SQL, OAuth credentials, least-privilege tests, benchmark SQL for every Genie question, explicit redaction, and refusal to claim improvement when evaluation did not support it.

One concrete iteration began with the generated corpus of 120,000 synthetic claims across 12 periods; after separating generated inventory from released pipeline coverage, live evidence correctly reports 110,000 released claims across 11 periods instead of presenting the full corpus as processed coverage.

The complete attempt, failure, change, rationale, and verification history is in [`BUILD_LOG.md`](BUILD_LOG.md), and approved trade-offs are in [`DECISIONS.md`](DECISIONS.md).

## Repository Layout

```text
resources/              Bundle resources for pipelines, jobs, governance, Lakebase, and the App
src/data/               Deterministic synthetic source generation and holdout release
src/pipeline/           Lakeflow bronze, silver, reconciliation, and gold SQL
src/governance/         Unity Catalog policies and effective-permission probes
src/ai/                 Explainable scoring, generated explanations, and evaluation
src/serve/              OAuth-authenticated Lakebase schema and upsert
src/genie/              Reproducible Genie definition, benchmarks, and results
src/app/                AppKit/React operational application
src/orchestration/      Cross-system verification notebook
tools/                  Genie, app, and live evidence automation
evidence/               Plain-text proof regenerated from the live workspace
```

Start with [`evidence/README.md`](evidence/README.md) for the evaluator-readable proof index.

## Run It

Prerequisites: Databricks CLI authentication for the `vandelay` profile and access to the configured workspace resources. No static Lakebase password is required.

```bash
databricks bundle validate --strict -t dev --profile vandelay
databricks bundle deploy -t dev --profile vandelay
databricks bundle run rebate_fraud_orchestration -t dev --profile vandelay
python3 tools/generate_evidence.py --profile vandelay
```

To regenerate one evidence file:

```bash
python3 tools/generate_evidence.py --profile vandelay --only=03_business_results.md
```

The evidence generator queries the live workspace, Lakebase, Genie, Jobs, Pipelines, SQL warehouse, and App; it writes plain-text Markdown and redacts identities, contact fields, entity names, credentials, and tokens.
