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
