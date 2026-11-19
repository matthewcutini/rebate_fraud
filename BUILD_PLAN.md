# FE Bar Build Plan

## 0. Build-Stopping Preflight

Verify that the SQL warehouse is serverless and supports AI Functions, that the selected `system.ai.*` model service is available, and that the CLI is upgraded from `v1.19.0` to at least `v1.20.0` before selecting AppKit execution identity modes.

## 1. Connected Data Flow

```text
Synthetic files in /Volumes/vandelay/rebate_fraud/raw_rebate_fraud/
  medical_claims/*.json ---------------------> bronze_medical_claims ---------+
  pharmacy_claims/*.json --------------------> bronze_pharmacy_claims --------+--> silver_claims --------+
  manufacturer_sales/*.csv -----------------> bronze_manufacturer_sales ------+                          |
  wholesaler_shipments/*.csv ---------------> bronze_wholesaler_shipments ----+--> silver_product_movement|
  pharmacy_reference/*.json ----------------> bronze_pharmacy_reference ------+--> silver_pharmacy_entities
                                                                                                          |
  malformed/invalid records <---------------- quarantine_claims <-------------- Lakeflow expectations     |
                                                                                                          v
                              gold_case_features <--- entity links + channel overlap + purchase reconciliation
                                      |
                                      | governed by Unity Catalog grants, comments, lineage and views
                                      v
                         vw_investigator_case_features
                                      |
                                      v
                 explainable score + ai_query grounded explanation job
                         |                              |
                         v                              v
                 gold_fraud_cases              gold_ai_evaluations
                         |
                         | idempotent upsert by case_id
                         v
                 Lakebase schema rebate_ops
                  cases  <----> case_events
                    |           case_communications
                    |           sync_state
                    |
                    +--> snapshot job --> gold_case_activity
                                           |
                          +----------------+----------------+
                          |                                 |
                          v                                 v
                Genie Agent reads                 Node/AppKit application
                gold_fraud_cases,                 reads gold metrics/Genie and
                gold_case_activity,               reads/writes Lakebase cases,
                gold_fraud_metrics                communications and escalation
                          |                                 |
                          +---------- embedded Genie -------+
```

Deleting a stage breaks the journey: without Lakeflow there are no conformed claims; without Unity Catalog there is no governed identity or access boundary; without AI there is no prioritized case or explanation; without Lakebase there is no mutable investigation record; without Genie the SVP loses governed ad hoc analysis; without the App investigators cannot act on cases or preserve the paper trail.

## 2. Stage Plans

### Lakeflow Spark Declarative Pipeline

- **Story:** Gives the SVP one reconciled view of claims, purchases, wholesaler movements, and changing pharmacy identities instead of separate channel files.
- **Inputs:** Raw files under `/Volumes/vandelay/rebate_fraud/raw_rebate_fraud/`.
- **Outputs:** `vandelay.rebate_fraud.bronze_medical_claims`, `bronze_pharmacy_claims`, `bronze_manufacturer_sales`, `bronze_wholesaler_shipments`, `bronze_pharmacy_reference`, `quarantine_claims`, `silver_claims`, `silver_product_movement`, `silver_pharmacy_entities`, and `gold_case_features`.
- **Features:** Serverless Lakeflow Spark Declarative Pipeline; SQL; Auto Loader through `STREAM read_files`; append flows for the two claims channels; expectations; `_metadata.file_path`; materialized views for conformed joins and aggregations; deterministic `case_id`; idempotent incremental processing.
- **Quality policy:** Quarantine missing claim IDs, non-positive quantities, and unparseable service dates; warn on late files and missing phone/fax; fail the update on incompatible schema drift or an empty critical claims source.
- **Verification:** Run twice, confirm the second run creates no duplicate claim IDs, query row counts and expectation metrics, and reconcile known planted cases.
- **Evidence:** `evidence/P01_lakeflow_run.txt` and `evidence/P01_lakeflow_quality_results.csv`.

### Unity Catalog

- **Story:** Gives the SVP consistent definitions and auditable access for pharmacy identity, claimed units, purchased units, suspected fraud, verified fraud, and recoveries.
- **Inputs:** All pipeline tables, especially `vandelay.rebate_fraud.gold_case_features`.
- **Outputs:** Governed tables plus `vandelay.rebate_fraud.vw_investigator_case_features`; table/column comments; grants for `rebate_svp`, `rebate_investigators`, and `rebate_legal` groups.
- **Features:** Managed volume, three-part names, lineage, least-privilege grants, a dynamic investigator view, and separate access-test service principal membership in the investigator group.
- **Access:** SVP sees metrics and all cases; investigators see assigned operational evidence and contact fields; legal sees escalated cases and their communications only.
- **Verification:** `SHOW GRANTS`, lineage read-back, positive investigator query, and denied query against SVP-only recovery detail using the non-admin service principal.
- **Evidence:** `evidence/P02_uc_lineage.txt`, `evidence/P02_uc_grants.txt`, and `evidence/P05_access_test.txt`.

### Intelligent Step: Explainable Score and GenAI

- **Story:** Prioritizes cases the SVP's team should investigate and explains the evidence without making the final fraud decision.
- **Inputs:** `vandelay.rebate_fraud.gold_case_features` and the fixed held-out labels used only for evaluation.
- **Outputs:** `vandelay.rebate_fraud.gold_fraud_cases` and `vandelay.rebate_fraud.gold_ai_evaluations`.
- **Features:** Explainable SQL score using identity similarity, cross-channel overlap, and excess claimed quantity; `ai_query` against an approved `system.ai.*` service for a structured explanation and outreach draft; `failOnError => false`; persisted output so inference runs once per case.
- **Verification:** Compare with the preregistered baseline on the held-out month; verify every explanation cites only supplied case features; report top-20 precision and unsupported-claim rate.
- **Evidence:** `evidence/P03_ai_scoring_results.csv`, `evidence/P03_ai_evaluation.json`, and `evidence/P03_ai_examples.txt`.

### Lakebase Operational Serving

- **Story:** Preserves the live investigation state, pharmacy outreach, responses, recoveries, and legal escalation trail that analytics tables alone cannot safely edit.
- **Inputs:** `vandelay.rebate_fraud.gold_fraud_cases`.
- **Outputs:** Lakebase `rebate_ops.cases`, `rebate_ops.case_events`, `rebate_ops.case_communications`, and `rebate_ops.sync_state`; periodic snapshot `vandelay.rebate_fraud.gold_case_activity`.
- **Features:** Lakebase Postgres Autoscaling; dedicated app-owned schema; OAuth connectivity; parameterized SQL; idempotent `INSERT ... ON CONFLICT (case_id) DO UPDATE` limited to machine-owned columns; immutable event records; human-owned status, notes, and decisions preserved.
- **Verification:** Upsert the same case set twice, confirm stable counts and preserved human edits, then read the deployed rows back from Lakebase and compare the UC activity snapshot.
- **Evidence:** `evidence/P04_lakebase_upsert.json` and `evidence/P04_lakebase_readback.txt`.

### Genie Agent

- **Story:** Lets the SVP ask governed questions about exposure, verified cases, recovery, channels, aging, and escalations without requesting a new report.
- **Inputs:** `vandelay.rebate_fraud.gold_fraud_cases`, `gold_case_activity`, and `gold_fraud_metrics`.
- **Outputs:** A curated Genie Agent configuration and conversation responses; no independent data copy.
- **Features:** Curated instructions, verified sample SQL, business synonyms, benchmark questions, serverless SQL warehouse, and AppKit Genie integration.
- **Verification:** Run fixed questions for total exposure, top suspicious entities, cross-channel cases, investigation aging, and recovered dollars; inspect generated SQL and results.
- **Evidence:** `evidence/P06_genie_questions.json` and `evidence/P06_genie_results.txt`.

### Node/AppKit Databricks App

- **Story:** Gives investigators one operational workflow while giving the SVP an executive view and embedded access to governed Genie analysis.
- **Inputs:** Analytics queries over `vandelay.rebate_fraud.gold_fraud_metrics` and `gold_fraud_cases`; Genie Agent responses; Lakebase `rebate_ops` tables.
- **Outputs:** Human case status, communications, recovery entries, and escalation events in Lakebase; no direct mutation of synced analytical tables.
- **Features:** Node.js, TypeScript, React, AppKit, analytics and Lakebase capabilities derived from `databricks apps manifest`, Genie integration, service-principal resource access, server-side pagination, and required loading/empty/error/stale states.
- **Screens:** (1) Executive Summary with exposure, verified fraud, recoveries, freshness, and embedded Genie; (2) Case Queue with filters and server-side pagination; (3) Case Detail with evidence, explanation, outreach, response, and event trail; (4) Legal Escalations with escalation reason and complete paper trail; (5) Pharmacy entity matching to help deduplicate pharmacies.
- **Trust:** Show signed-in identity, generated Genie SQL, streaming/error status, data freshness, source, and an “AI-generated—verify” disclosure.
- **Verification:** AppKit validation, type generation, updated Playwright smoke tests, deployed app status read-back, API read/write test, and UI smoke test using synthetic cases.
- **Evidence:** `evidence/P07_app_validate.txt`, `evidence/P07_app_smoke.txt`, and `evidence/P07_app_api_readback.json`.

## 3. Table List

### Bronze: Raw as Landed

Every bronze table includes `source_file_name` and `load_timestamp`.

| Table | Grain | Purpose |
|---|---|---|
| `bronze_medical_claims` | One row per medical-channel claim line as received | Preserve medical claim payloads and source metadata. |
| `bronze_pharmacy_claims` | One row per pharmacy-channel claim line as received | Preserve pharmacy claim payloads and source metadata. |
| `bronze_manufacturer_sales` | One row per manufacturer shipment or return line | Establish direct product movement evidence. |
| `bronze_wholesaler_shipments` | One row per wholesaler shipment or return line | Establish indirect product movement evidence. |
| `bronze_pharmacy_reference` | One row per source-system pharmacy identity version | Preserve openings, closures, aliases, addresses, phones, and fax numbers. |
| `quarantine_claims` | One row per rejected claim record | Preserve the failed row, source, rule, and reason. |

### Silver: Cleaned and Conformed

| Table | Grain | Purpose |
|---|---|---|
| `silver_claims` | One row per conformed claim line | Align medical and pharmacy field names and remove exact retransmissions. |
| `silver_product_movement` | One row per normalized shipment or return movement | Conform manufacturer and wholesaler units, dates, and source identities. |
| `silver_pharmacy_entities` | One row per source identity linked to a canonical pharmacy | Store explainable match features and canonical entity assignment. |

### Gold: Business Ready

| Table | Grain | Purpose |
|---|---|---|
| `gold_case_features` | One row per pharmacy, product, and review period | Combine claimed units, purchased units, cross-channel overlap, and identity evidence. |
| `gold_fraud_cases` | One row per stable fraud case | Store explainable score, reasons, exposure, AI explanation, and outreach draft. |
| `gold_case_activity` | One row per Lakebase case event | Return operational outcomes and communications metadata to governed analytics. |
| `gold_fraud_metrics` | One row per reporting period and business slice | Provide exposure, verified-case, recovery, aging, channel, and region metrics. |
| `gold_ai_evaluations` | One row per method, evaluation run, and metric | Preserve baseline and candidate results against the locked protocol. |

## 4. Bundle Layout

```text
databricks.yml
resources/
  rebate_fraud.pipeline.yml
  rebate_fraud.job.yml
  access_test.job.yml
  rebate_fraud.app.yml
src/
  data/generate_raw.py
  pipeline/bronze.sql
  pipeline/silver.sql
  pipeline/gold_features.sql
  governance/apply_grants.sql
  ai/score_and_explain.sql
  serve/upsert_lakebase.py
  serve/snapshot_lakebase.py
  genie/serialized_space.json
  app/
```

`databricks.yml` will define one target and variables for `catalog`, `schema`, `raw_volume`, `warehouse_id`, `ai_model_service`, `app_name`, `genie_space_id`, `lakebase_project`, `lakebase_branch`, `lakebase_database`, and `access_test_service_principal`. App names use a dedicated variable and must resolve to a valid, namespaced name of at most 30 lowercase characters, digits, or hyphens.

Bundle resources are one serverless pipeline, the main serverless STANDARD job, a small service-principal access-test job, and one App. Lakebase Autoscaling project creation and synced-table APIs are not currently supported as modern DAB resources; the plan therefore requires an approved existing project or a separately approved CLI provisioning step, followed by bundle-managed schema/upsert tasks. This exception must be recorded rather than hidden.

## 5. Orchestration

The main `rebate_fraud_job` uses a manual trigger for reproducible evidence and this task order:

1. `generate_raw_files` — create deterministic synthetic source files in the UC volume.
2. `run_lakeflow_pipeline` — ingest and produce bronze, silver, and `gold_case_features`.
3. `score_and_explain` — create `gold_fraud_cases` and `gold_ai_evaluations`.
4. `upsert_lakebase_cases` — upsert machine-owned fields and preserve human edits.
5. `snapshot_lakebase_activity` — publish operational events to `gold_case_activity`.
6. `refresh_gold_metrics` — create or refresh `gold_fraud_metrics`.
7. `evaluate_locked_protocol` — execute baseline and candidate evaluation against the held-out month.
8. `capture_text_evidence` — write row counts, IDs, quality results, metrics, and task summaries under `evidence/`.

Every notebook or Python task emits the required short JSON summary. The separate `rebate_fraud_access_test` runs as the approved investigator service principal and writes P05 positive and negative access results. Genie and App deployment occur after the governed tables exist, and both are read back after deployment.

## 6. Four-to-Eight-Hour Time Plan

| Work | Time | Exit criterion |
|---|---:|---|
| Preflight and bundle skeleton | 0.5 hour | Lakebase, serverless warehouse, model service, AppKit manifest, and CLI prerequisites verified. |
| Deterministic synthetic files | 0.5 hour | Five source folders contain coherent data and planted fraud cases. |
| Lakeflow bronze/silver/gold features | 1.25 hours | Pipeline reruns without duplicates and quality rules produce expected results. |
| Unity Catalog governance and P05 | 0.5 hour | Grants, lineage, allowed query, and denied query captured. |
| Explainable score, AI output, evaluation | 0.75 hour | Held-out results and grounded examples persisted. |
| Lakebase schema, upsert, snapshot | 0.75 hour | Repeat upsert preserves a human edit and snapshot matches. |
| Genie Agent | 0.5 hour | Fixed questions return verified SQL results. |
| Node/AppKit app | 1.5 hours | Four screens, Lakebase write-back, Genie trust elements, and smoke tests work. |
| Evidence, rerun, and read-back | 0.75 hour | Main job succeeds, deployed objects are read back, and text evidence is committed. |
| **Total** | **7.0 hours** | Connected journey is reproducible and evidenced. |

Scope protection: if the build exceeds eight hours, reduce styling and secondary metrics first. Do not remove a required platform stage, the held-out evaluation, the P05 access test, or text evidence.
