# Decisions

> `[YOUR WORDS]` Rewrite each decision and rationale in your own words before submission.

## 2026-11-17 — Rebate Fraud Use Case

- **Decision:** Focus the prototype on pharmacy rebate overclaims, cross-channel duplicate claims, changing pharmacy identities, investigation communications, recoveries, and legal escalation.
- **Options considered:** A generic operational-improvement story; a narrow duplicate-claim detector; an end-to-end rebate fraud prevention workflow.
- **Why:** `[YOUR WORDS]` The end-to-end workflow connects fraudulent payment detection to a measurable recovery outcome and preserves the required paper trail.

## 2026-11-17 — AI Approach

- **Decision:** Use a hybrid approach: fuzzy entity resolution, explainable anomaly or risk scoring, and grounded GenAI assistance for outreach and legal case summaries.
- **Options considered:** Rules and fuzzy matching only; supervised ML; the hybrid approach.
- **Why:** `[YOUR WORDS]` The hybrid approach supports changing pharmacy identities and explainable prioritization without allowing AI to make final fraud or legal decisions.

## 2026-11-17 — Value Hypothesis

- **Decision:** Use a balanced recovery target of 25% of the estimated $10 million annual fraudulent overpayment exposure, producing an illustrative $2.5 million annual value.
- **Options considered:** Conservative 10% recovery; balanced 25% recovery; ambitious 40% recovery.
- **Why:** `[YOUR WORDS]` The balanced target is material but remains explicitly labeled as an assumption requiring validation.

## 2026-11-17 — Data Sources

- **Decision:** Use synthetic, vendor-neutral representations of manufacturer sales, wholesaler distribution, 867 distribution, rebate claims, pharmacy identity, and investigation workflow data.
- **Options considered:** Name real source vendors; omit wholesaler data; use vendor-neutral synthetic source systems including wholesalers.
- **Why:** `[YOUR WORDS]` Wholesaler records are necessary to reconcile product movement with rebate quantities while vendor-neutral synthetic data protects confidentiality and meets FE Bar rules.

## 2026-11-17 — Build Design

> `[REWRITE IN YOUR WORDS]` Rewrite these decisions and reasons before submission.

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

- **Decision:** `[REWRITE IN YOUR WORDS]` Treat Lakebase availability in the GCP workspace as a build-stopping preflight. If unavailable, use a workspace with supported Lakebase access or obtain approved preview access; do not silently substitute another database.
- **Alternative considered:** Replace Lakebase with another operational store to keep building.
- **Why:** `[REWRITE IN YOUR WORDS]` Lakebase is a required stage of the connected FE Bar journey, and a substitute would misrepresent the architecture.

## 2026-11-18 — Intelligent Rebate-Fraud Step [REWRITE IN YOUR WORDS]

- **Decision:** Use a deterministic explainable score with named point components and drivers on every case, then use structured `ai_query` only for the top 20 cases to draft an explanation and next action.
- **Options considered:** Explainable score plus targeted GenAI; a supervised model tracked with MLflow; text classification or extraction only.
- **Why:** The selected approach fits the build time box, keeps prioritization auditable, limits model cost, and avoids defending a classifier trained only on synthetic labels.
