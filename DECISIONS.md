# Decisions

## 2026-11-17 — Rebate Fraud Use Case

- **Decision:** Focus the prototype on pharmacy rebate overclaims, cross-channel duplicate claims, changing pharmacy identities, investigation communications, recoveries, and legal escalation.
- **Options considered:** A generic operational-improvement story; a narrow duplicate-claim detector; an end-to-end rebate fraud prevention workflow.
- **Why:** The end-to-end workflow connects fraudulent payment detection to a measurable recovery outcome and preserves the required paper trail. This is operational data that the rebate fraud team can use to collaborate and enhance their efforts far more than they've ever been able to when working from various spreadsheets.

## 2026-11-17 — AI Approach

- **Decision:** Use a hybrid approach: fuzzy entity resolution, explainable anomaly or risk scoring, and grounded GenAI assistance for outreach and legal case summaries.
- **Options considered:** Rules and fuzzy matching only; supervised ML; the hybrid approach.
- **Why:** The hybrid approach supports changing pharmacy identities and explainable prioritization without allowing AI to make final fraud or legal decisions.

## 2026-11-17 — Value Hypothesis

- **Decision:** Use a balanced recovery target of 25% of the estimated $10 million annual fraudulent overpayment exposure, producing an illustrative $2.5 million annual value.
- **Options considered:** Conservative 10% recovery; balanced 25% recovery; ambitious 40% recovery.
- **Why:** This is an early version of the app. As the app evolves its capabilities, it may be able to recover higher amounts of fraudulent overpayments.

## 2026-11-17 — Data Sources

- **Decision:** Use synthetic, vendor-neutral representations of manufacturer sales, wholesaler distribution, 867 distribution, rebate claims, pharmacy identity, and investigation workflow data.
- **Options considered:** Name real source vendors; omit wholesaler data; use vendor-neutral synthetic source systems including wholesalers.
- **Why:** Wholesaler records are necessary to reconcile product movement with rebate quantities while vendor-neutral synthetic data protects confidentiality and meets FE Bar rules.

## 2026-11-17 — Build Design

| Decision | Choice | Alternative considered | Reason |
|---|---|---|---|
| Ingestion | UC volume files with Auto Loader | Generate rows directly in pipeline tables | Files preserve a visible raw-ingestion stage and demonstrate incremental and late-file handling. |
| Source conforming | Separate medical and pharmacy feeds merged in silver; sales and wholesaler feeds provide purchase evidence | One consolidated claims feed | Separate channels prove conforming and enable the cross-channel fraud scenario. |
| Data quality | Quarantine invalid critical rows, warn on late/contact issues, fail on schema drift or empty critical input | Warn on nearly every issue | The selected policy demonstrates governed handling without allowing structural failures to pass silently. |
| Governance | SVP, investigator, and legal personas with least privilege | SVP and investigator only | Legal-only access to escalated cases makes the paper trail and escalation workflow credible. |
| P05 identity | Dedicated service principal in the investigator group | Dedicated non-admin workspace user | A service principal makes positive and negative access tests repeatable. |
| Lakebase | Idempotent job upsert preserving human-owned fields | Synced gold table plus separate edits | The upsert pattern keeps one operational case while protecting investigator edits. |
| Intelligent step | Explainable fuzzy score plus `ai_query` explanations | Add a trained classifier | The selected method fits the time box and avoids defending a model trained on synthetic labels. |
| AI evaluation | Fixed synthetic gold set with structured groundedness checks | Small manual rubric only | Structured checks are reproducible and still allow a fixed human readability review. |
| Evaluation protocol | Temporal holdout, exact-match baseline, top-20 precision, decision-time cutoff, and explicit no-claim threshold | Random holdout with F1 | The selected protocol matches investigator capacity and prevents future information leakage. |
| App | Node.js, TypeScript, React, and AppKit | Python Streamlit | AppKit provides the requested polished operational workflow and embedded governed data/Genie experience, accepting additional implementation time. |
| Trigger | Manual bundle job run | File-arrival trigger | Manual execution is deterministic for evaluator evidence and avoids timing risk. |

## 2026-11-17 — Lakebase Feasibility Gate

- **Decision:** Use Lakebase in the GCP workspace provided.
- **Alternative considered:** Use an AWS or Azure workspace.
- **Why:** Lakebase is available in GCP workspaces.

## 2026-11-18 — Lakeflow Data Quality Policy Using Expectations

- **Decision:** Drop and quarantine claims with missing identifiers, non-positive requested units, invalid service dates, unknown product codes, or exact retransmissions; warn and retain late claims, trimmed names, and missing phone or fax values; fail the update on manifest mismatches, incompatible schema drift, or empty critical claims input.
- **Options considered:** Warn and retain every defect; fail on every defect; use severity-based handling tied to whether a record can be traced and reconciled.
- **Why:** Severity-based handling preserves explainable evidence without allowing structurally unreliable or unreconcilable claims into business results.

## 2026-11-18 — Unity Catalog Access Model [REWRITE IN YOUR WORDS]

- **Decision:** Govern a separate consumption table with data-driven regional row access and sensitive-contact masking. The SVP sees all regions with contact fields masked, the Director sees all regions with contact fields visible, and a regional analyst sees only an assigned region with contact fields visible. Legal-only case filtering will be added when legal escalation status exists in the operational case table.
- **Options considered:** Regional row filtering; assignment-based filtering dependent on Lakebase; national access with masking only.
- **Why:** Regional scope is realistic, independently demonstrable now, and does not make pipeline output depend on the identity that runs the pipeline.

## 2026-11-18 — Governance Test Identity [REWRITE IN YOUR WORDS]

- **Decision:** Create and use the dedicated non-admin service principal `febar-rebate-governance-test` for effective-permission tests.
- **Options considered:** Reuse a project service principal; reuse a broader non-admin principal; create a dedicated principal.
- **Why:** A dedicated identity makes positive, masked, denied, and cleanup checks repeatable without relying on administrator group membership.

## 2026-11-18 — Intelligent Rebate-Fraud Step [REWRITE IN YOUR WORDS]

- **Decision:** Use a deterministic explainable score with named point components and drivers on every case, then use structured `ai_query` only for the top 20 cases to draft an explanation and next action.
- **Options considered:** Explainable score plus targeted GenAI; a supervised model tracked with MLflow; text classification or extraction only.
- **Why:** The selected approach fits the build time box, keeps prioritization auditable, limits model cost, and avoids defending a classifier trained only on synthetic labels.

## 2026-11-18 — Lakebase Operational Record Model [YOUR WORDS]

- **Decision:** Use a Lakeflow Job to upsert machine-owned fields from `gold_fraud_cases` into one mutable Lakebase case record while preserving investigator-owned status, owner, priority, notes, due date, decision, recovery, and legal-escalation fields. Record every actual insert or update with a PostgreSQL trigger.
- **Options considered:** A read-only synced table; separate read-only source and human-edit tables joined by the app; one operational case table with column-limited upserts and immutable history.
- **Why:** The selected pattern gives investigators one current case without allowing an analytics refresh to erase their work, while the trigger produces a database-enforced paper trail for every actual change.

## 2026-11-18 — Lakebase Access Boundary [YOUR WORDS]

- **Decision:** Use Unity Catalog policies for governed Delta analytics; use Lakebase connection, schema, table, constraint, and trigger controls for the operational store; enforce investigator assignment, legal-only row visibility, workflow transitions, and field-level permissions in the app.
- **Options considered:** Treat Unity Catalog policies as if they covered Lakebase rows; implement PostgreSQL row-level security immediately; use explicit app authorization over least-privilege Postgres grants.
- **Why:** Unity Catalog row filters and masks do not automatically propagate into Postgres. App authorization is the clearest prototype boundary, while PostgreSQL RLS remains a future hardening option.

## 2026-11-18 — Genie Governed Source Design [YOUR WORDS]

- **Decision:** Build the executive Genie space only on `governed_case_features`, exclude sensitive contact columns, and replace questions that require unavailable fraud outcomes or AI scores with governed exposure, reconciliation, identity, trend, drill-down, and completeness questions.
- **Options considered:** Use several ungoverned gold tables; mix a metric view with its base table; use one row-filtered and masked governed gold table.
- **Why:** The single governed source preserves Unity Catalog row filters and masks, avoids ambiguous duplicate semantics, and prevents Genie from presenting suspected exposure as verified fraud or recovery.

## 2026-11-18 — Databricks App Experience [YOUR WORDS]

- **Decision:** Use an operational investigation console with four screens: Operations Overview, Priority Case Queue, Case Workspace, and Ask Genie. Use persona lenses to change emphasis without changing authorization.
- **Options considered:** Executive dashboard; operational investigation console; minimal neutral workspace; a fifth CustomerLake entity-verification screen.
- **Why:** The operational console connects governed analytics to action and a complete Lakebase paper trail. CustomerLake was removed when the requested workspace capability was confirmed unavailable.

## 2026-11-18 — App Execution Identity [YOUR WORDS]

- **Decision:** Execute SQL warehouse and Genie requests on behalf of the signed-in user, while using the app service principal only for the shared Lakebase operational schema.
- **Options considered:** App service principal for every request; signed-in user for every resource; mixed identity by resource.
- **Why:** Mixed identity preserves Unity Catalog row filters and masks for analytics while retaining controlled shared write access to operational case records and database-enforced history.

## 2026-11-19 — Connected Job Trigger [YOUR WORDS]

- **Decision:** Use one manually triggered Lakeflow Job with explicit serial dependencies from pipeline refresh through governed consumption, scoring, AI evaluation, Lakebase sync, and connected-output verification. Limit it to one concurrent run and queue overlapping requests.
- **Options considered:** File arrival on a final manifest; a recurring schedule; manual execution.
- **Why:** Manual execution keeps the fixed demo evidence reproducible and prevents late data from changing the deck, while the dependency graph, queue, and rerun proof still demonstrate production-safe orchestration.

## 2026-11-23 — Business Deck Story [YOUR WORDS]

- **Decision:** Use the approved business narrative that moves from visible suspected exposure to a bounded pilot for verified outcomes, with separate operating and executive value for the Director of Rebate Operations and the SVP of Contracting, Rebates.
- **Options considered:** A technology-led architecture deck; a narrow fraud-detection demo deck; an outcome-led business deck with the answer up front, demo setup, persona KPIs, transparent value logic, trust, architecture, pilot, and close.
- **Why:** The outcome-led structure makes the customer decision clear while preserving the distinction between suspected exposure, verified fraud, recoverable value, and realized recovery.

## 2026-11-23 — Business Deck Value Framing [YOUR WORDS]

- **Decision:** Show the value case as a formula only: $9,823,195.85 measured suspected exposure × verified-fraud rate × achievable recovery rate = recovery value, with both rates measured in the pilot and no illustrative dollar result.
- **Options considered:** Formula only; formula plus an illustrative 25% planning-target example ($2,455,798.96); the customer-stated $10M × 25% = $2.5M.
- **Why:** Every number on the slide comes from live evidence in `evidence/HEADLINES.md`, so no recovery figure is claimed before human-adjudicated pilot outcomes exist.

## 2026-11-23 — Business Deck Build Route [YOUR WORDS]

- **Decision:** Rebuild the approved 12-slide deck on a copy of the "*TEMPLATE Databricks Corporate Slide 2025" Google Slides template and export it to PDF, replacing the Markdown fallback.
- **Options considered:** Retry on the corporate template; keep the Markdown-to-PDF fallback.
- **Why:** The earlier failure came from exporting the full template; copying it inside Drive and exporting only the finished 12-slide deck stays within the connector's limits and gives the evaluator a template-branded deck.
