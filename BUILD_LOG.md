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

## 2026-11-19 — Live Evidence Generator

- **Tried:** Built one SDK-based generator for pipeline, SQL, Jobs, Genie, Lakebase, and app proof with per-file regeneration, Markdown tables, final-run anchoring, and identity/secret redaction.
- **Failed:** The first data-quality query used obsolete reconciliation column names; the first AI query used `ai_prompt_version` instead of `prompt_version`; the first two live Genie comparisons treated harmless display-label differences as mismatches; one SDK-version diagnostic referenced an unavailable module attribute.
- **Changed:** Aligned queries to the deployed schemas, normalized harmless Genie labels without weakening numeric comparison, omitted free-form Genie prose that repeated synthetic entity names, and retained structured SQL/results as the answer proof.
- **Why:** Evaluators need live, readable, reproducible text evidence without secrets, identities, raw encoded notebook exports, or hand-entered result values.
- **Verified:** `tools/generate_evidence.py` compiled and regenerated all stage files from `--profile vandelay`; the final Genie run matched 15 of 15 benchmarks; privacy scans found no emails, tokens, or synthetic entity names; `git diff --check` passed.

## 2026-11-19 — Evaluator README

- **Tried:** Drafted an outcome-first repository README linking the customer problem, delivered outcomes, value boundaries, connected stages, approved trade-offs, AI-assisted workflow, repository layout, run commands, and live evidence.
- **Failed:** The rewritten headline rounded the approved exposure figure and described suspected exposure as already caught and mitigated, which exceeded the evidence.
- **Changed:** Restored the exact approved monetary value and described it as simulated suspected rebate overpayment exposure surfaced for investigation.
- **Why:** The evaluator should see the customer outcome immediately without confusing suspected exposure with verified fraud, prevented loss, or recovered cash.
- **Verified:** The final README contains no rewrite markers; all quantitative business claims match `evidence/HEADLINES.md`; every connected stage links to implementation and proof; `git diff --check` passes.

## 2026-11-23 — Business Deck

- **Tried:** Built the approved outcome-led business deck for rebate operations and contracting leadership using the corporate Slides template as the preferred source.
- **Failed:** The exact Google Slides template was available in Drive, but its exported presentation exceeded the Drive connector's file-size limit. The first Markdown PDF renderer lacked its Python dependency, and the dependency-enabled retry lacked native GObject libraries. The first PDF flow slide also rendered unsupported arrow glyphs, and one later image-rendering dependency fetch returned HTTP 403.
- **Changed:** Used the explicitly approved Markdown fallback; created a Databricks-styled widescreen PDF with DM Sans and corporate colors; replaced glyph arrows with drawn connectors; reused the cached offline image renderer after the network fetch failure.
- **Why:** The fallback preserves a readable FE Bar artifact, speaker notes, evidence-only numbers, and visual quality without bypassing the managed Google Drive connector.
- **Verified:** The PDF contains the approved business story and evidence-only quantitative claims; all pages were rendered to images and visually inspected; no overlapping or cut-off text remained after the connector fix.

## 2026-11-23 — Business Deck on the Corporate Template

- **Tried:** Rebuilt the approved 12-slide outline on a Drive copy of the "*TEMPLATE Databricks Corporate Slide 2025" template with `deck/build_gslides.py`, using only the template's light-master layouts, DM Sans and theme colours, and the formula-only value case.
- **Failed:** The first trash call on the draft copy returned HTTP 404 because Drive places copies of a shared-drive file in that shared drive, and the call omitted shared-drive support. The skill validator reported 8 `text_style_off_by_one` errors that were deliberate large numerals ("11" and step numbers), not styling defects. The first render had regular-weight titles, an unbalanced cover subtitle, and excess empty space on two slides.
- **Changed:** Copied the final deck into My Drive and moved both shared-drive copies to the trash; switched content titles to bold 28 pt; line-broke the cover subtitle; tightened the problem panel and trust cards; rebuilt on a fresh template copy and re-exported.
- **Why:** The deck must follow the corporate template, stay private until sharing is approved, and keep every number traceable to `evidence/HEADLINES.md`.
- **Verified:** Each new slide was inserted directly after a light-master template slide and then moved into place; all 54 template sample slides were removed. The PDF export (12 pages) was rendered page by page and visually inspected, with no overlapping or cut-off text. All body text is 15 pt or larger. All 12 slides carry `[YOUR WORDS]` speaker notes. The only figures on the slides are $9,823,195.85, 110,000, 11 and 21,845 plus the 2026-11-19 measurement date. The final PDF is `deck/rebate_fraud_business_deck.pdf`; the earlier Markdown-route deck, its PDF, stylesheet, fonts and renderer were removed so the repository holds one deck.
