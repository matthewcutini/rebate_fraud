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
