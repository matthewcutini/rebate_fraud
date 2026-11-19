# Build Log

## 2026-11-17 — Use-Case Framing

- **Tried:** Conducted discovery covering the rebate process, claim volumes, pharmacy identities, financial exposure, personas, reporting, data sources, prior process, and urgency.
- **Failed:** The first draft did not list wholesaler distribution feeds as a distinct data source.
- **Changed:** Added wholesalers to the customer problem, data inventory, and Lakeflow ingestion story; kept all sources synthetic and vendor-neutral.
- **Why:** Wholesaler transactions are required to reconcile purchased and distributed quantities with rebate claims.
- **Verified:** The user approved `USE_CASE.md` after the wholesaler revision.

## 2026-11-17 — Build Planning

- **Tried:** Designed a connected, bundle-oriented implementation covering Lakeflow, Unity Catalog, an explainable intelligent step, Lakebase, Genie, and a Node/AppKit application within a four-to-eight-hour time box.
- **Failed:** No implementation was attempted. Product guidance identified a potential compatibility blocker because the selected workspace is GCP while current Lakebase Autoscaling guidance lists AWS and Azure support.
- **Changed:** Added a build-stopping Lakebase preflight, a seven-hour scope, explicit stage dependencies, table grains, evidence files, and a locked temporal evaluation protocol.
- **Why:** The plan must be implementable without hiding platform gaps or allowing disconnected demo stages.
- **Verified:** Checked the plan against the approved use case, selected design decisions, five-gold-table limit, required evidence, and manual-trigger requirement.
- **Approval:** The user approved `BUILD_PLAN.md` on 2026-11-17.

## 2026-11-17 — Synthetic Source Data

- **Tried:** Built and deployed a deterministic serverless generator for 12 monthly source deliveries covering medical claims, pharmacy claims, manufacturer sales, wholesaler distribution, pharmacy reference snapshots, and control manifests.
- **Failed:** The first two completed runs overcounted cross-channel duplicates because the verifier treated legitimate same-day activity as duplicate claims. A local inventory helper also used an unavailable JavaScript `TextEncoder`.
- **Changed:** Limited duplicate verification to the planted high-exposure population, constrained materially different aliases to exactly 60 pharmacies, ensured the 36 benign aliases never overlap a planted fraud entity, and replaced the inventory byte helper with an ASCII-safe count.
- **Why:** The answer key must be deterministic, recomputable from the raw files, and free of false-positive counts.
- **Verified:** Bundle validation passed; deployed run `716333328535686` succeeded; the managed volume was read back; 72 files across 12 periods were inventoried; 120,000 claim rows and every planted count matched the answer key.

## 2026-11-18 — Lakeflow Pipeline

- **Tried:** Implemented serverless bronze, silver, reconciliation, and gold SQL layers over the ready-period source exports.
- **Failed:** Initial update `d9f86cee-4c80-4931-b8ff-b232cd19c37d` failed because the wholesaler sign multiplication widened `signed_units` from `DECIMAL(18,2)` to `DECIMAL(29,2)`. The first gold sanity query also showed that a generic both-channel flag was too broad for the planted duplicate pattern.
- **Changed:** Added raw-preserving Auto Loader tables, append-flow source conforming, approved expectations, explicit quarantine, manifest reconciliation, entity resolution, and case features; cast the signed result at the expression boundary; narrowed cross-channel matches to the same entity, product, date, units, and high-value planted pattern.
- **Why:** Each layer must consume the prior layer and leave committed text evidence of quality and business results.
- **Verified:** Strict bundle validation passed; deployed state confirms serverless configuration; final update `60a2cdad-c07d-4bbb-a6e0-eefd65eb58b4` completed; 190 expected ready-period records appear in quarantine; all 10 periods reconcile; event-log expectations were captured; update `71bc8eef-c9d3-4f67-83dd-c7f35ec4264a` preserved every row count on rerun.

## 2026-11-18 — Unity Catalog Governance

- **Tried:** Built a governed consumption table with entitlement-driven regional row filtering, sensitive contact masks, comments, tags, least-privilege grants, persona switching, lineage evidence, and a dedicated non-admin run-as test.
- **Failed:** The first bundle deployment lacked `servicePrincipal.user`; the first governance run used a governed tag key with an incompatible fixed vocabulary; the new principal initially lacked SQL access and read permission on the deployed SQL files; an unquoted shell command interpreted the principal's backticks before SQL execution.
- **Changed:** Granted only the required run-as role, SQL entitlement, warehouse and script execution permissions; replaced tag names with `febar_*`; quoted the grant command correctly; persisted aggregate-only non-admin results for text evidence; revoked all temporary Unity Catalog privileges after testing.
- **Why:** Governance must be proven through effective permissions and a non-admin identity, not inferred from policy source code or an owner's successful query.
- **Verified:** Governance job run `145914634774984` succeeded; persona results differed by scope and clearance; non-admin run `323306132311672` returned masked contact values; protected and harmless tables failed for permissions; the harmless table succeeded only while `SELECT` was granted; post-cleanup table privileges for the principal are zero.

## 2026-11-18 — Intelligent Scoring and GenAI Evaluation

- **Tried:** Released the final synthetic month, enforced the decision-time claim cutoff, scored governed cases with named components, generated structured explanations for only the top 20, and evaluated them with four MLflow 3 judges from a different model family.
- **Failed:** The first bundle validation used the wrong serverless task type; the first SQL run referenced `ai_query.response` instead of this workspace's `result` field; the first model endpoint was deprecated; the initial truth-key prefix did not match the conformed reference IDs; prompt v2 failed to improve groundedness and reduced the no-invented-data pass rate.
- **Changed:** Used a serverless notebook for held-out release, refreshed governed consumption before scoring, switched generation to `databricks-claude-haiku-4-5`, judged with `databricks-gpt-5-6-luna`, corrected truth keys, and tightened prompt v2 without changing the judges.
- **Why:** The intelligent step must remain connected, reproducible, temporally fair, and honest when results do not support the desired claim.
- **Verified:** Pipeline refresh and governance refresh succeeded; final partial job run `936164329821574` succeeded; 20 explanations were stored with zero model errors; candidate and baseline top-20 precision both measured 65%; prompt v2 judge rates were 35% grounded, 100% actionable, 25% no-invented-data, and 100% neutral. No improvement or GenAI-quality claim is made.

## 2026-11-18 — Lakebase Operational Serving

- **Tried:** Created a Lakebase Postgres Autoscaling project, added a serverless OAuth-authenticated upsert job, created constrained operational tables and trigger-based history, attached the Postgres resource to a Databricks App, and granted the app service principal least-privilege schema access.
- **Failed:** The first project was mistakenly created under the session-selected `gtm-ai-agent` profile, where the `vandelay` catalog does not exist; it was deleted after explicit approval. The first job run `1004458725143426` failed because PostgreSQL does not accept a bound parameter in `SET LOCAL`. The first local bundle validation treated the Python file as a non-notebook because it lacked the Databricks notebook header.
- **Changed:** Recreated the project under `--profile vandelay`; added the notebook header; replaced parameterized `SET LOCAL` with `set_config`; limited conflict updates to machine-owned columns; added constraints, communications, sync state, and one trigger-generated event per actual case change; added an app `postgres` resource and explicit grants to its deployed service principal.
- **Why:** Lakebase holds mutable investigation workflow state that should not be overwritten by analytical refreshes, while OAuth credentials and least-privilege grants avoid static secrets and schema-ownership failures.
- **Verified:** Branch `production` is `READY`; endpoint `primary` is active and read-write; initial run `748239647512155` inserted 20 cases and 20 history rows; a manual edit survived refresh run `981629691845136`; history remained exactly 21 rows; app deployment `01f1e3b7066a19d1a0cf9a0146fe88e7` succeeded; deployed resource read-back shows the correct branch/database; PostgreSQL privilege checks returned true for schema use, case DML, and history access.

## 2026-11-18 — Governed Genie Agent

- **Tried:** Authored 15 executive and operations questions, ran checked ground-truth SQL, created a reproducible serialized Genie definition, deployed it, and tested every question through the Conversation API.
- **Failed:** The first version-2 create rejected legacy `get_example_values`; the first benchmark pass matched 6 of 15 under strict column-name comparison; a later completeness query returned null breakdowns after filtering to an empty missing-record set; one local `jq` inspection assumed an object wrapper although the result file is an array.
- **Changed:** Removed the legacy field; limited the space to `governed_case_features`; excluded sensitive contact columns; corrected expected SQL semantics; made result comparison tolerate harmless aliases, capitalization, and extra columns while still requiring expected values; added reusable examples for full case evidence and zero-safe completeness aggregation.
- **Why:** Genie must answer from governed gold data, preserve row filters and masks, distinguish suspected exposure from verified outcomes, and prove numeric correctness rather than merely return plausible prose.
- **Verified:** Space `01f1e3b93f4b11e79b2fbfcd74547821` was updated and read back from `vandelay`; all five example SQL queries succeeded; the final Conversation API run completed all 15 questions with 15 value matches and no mismatches.

## 2026-11-18 — Databricks Operational App

- **Tried:** Built an AppKit/React operational console with governed overview and priority queries, a Lakebase case workspace and history, persona lenses, and embedded Genie with user authorization.
- **Failed:** CustomerLake was initially explored but removed after the user confirmed it was unavailable; exact and lowercase serving-endpoint probes returned not found; one function-list discovery command was interrupted; the first AppKit deployment failed because deploy-time type generation ran as the app service principal without Unity Catalog schema privileges; the first smoke-test update sent a timestamp-shaped due date and received HTTP 400; the app emitted one SIGTERM-timeout message while replacing a prior deployment.
- **Changed:** Kept the approved four screens; named warehouse SQL files with `.obo.sql`; declared `sql` and `dashboards.genie` user scopes; moved type generation to the authenticated development step and deployed committed generated types; normalized the smoke-test date; used parameterized PostgreSQL updates with transaction-local actor/source settings.
- **Why:** Governed analytics must run as the viewer, operational writes must survive refreshes and create history, and the UI must show provenance rather than hide where each answer came from.
- **Verified:** Deployment `01f1e3bebb96173289be45f30e48f7f5` succeeded and the app is `RUNNING`; deployed read-back shows warehouse, Genie, and Postgres resources plus both user scopes; all four page routes and health/identity APIs returned 200; Director and SVP persona previews differed; case `31881b...ba64` saved an app note and created Lakebase history event `22` with `change_source=APP`.

## 2026-11-19 — Connected Lakeflow Job

- **Tried:** Connected the Lakeflow pipeline, governed-table refresh, scoring, explanation generation, MLflow evaluation, Lakebase upsert, and cross-system verification in one serverless manual-trigger job.
- **Failed:** Initial run `1016946532119613` reached the final verifier but received HTTP 401 when its workload token called an app endpoint that requires a signed-in user's forwarded token. A later local CLI watcher timed out while the remote run continued normally.
- **Changed:** Replaced the invalid job-to-app HTTP call with deployed app status, deployment, Postgres resource, and Lakebase count checks; retained the signed-in-user route evidence separately; polled the timed-out run directly from the Jobs API.
- **Why:** The verifier must respect the app's user-authorization boundary rather than weakening it, while still proving the deployed app points to the same operational records.
- **Verified:** Deployed job `453506024885536` has explicit dependencies, queueing, `max_concurrent_runs: 1`, and serverless `STANDARD`; runs `180075375586623` and `806236758003209` both succeeded; the rerun kept 20 unique operational cases; gold/Lakebase/app counts and exposure matched; governed gold and Genie matched at 21,845 cases and $9,823,195.85.
