# Build Log

## 2026-11-17 — Use-Case Framing

- **Tried:** Conducted discovery covering the rebate process, claim volumes, pharmacy identities, financial exposure, personas, reporting, data sources, prior process, and urgency.
- **Failed:** The first draft did not list wholesaler distribution feeds as a distinct data source.
- **Changed:** Added wholesalers to the customer problem, data inventory, and Lakeflow ingestion story; kept all sources synthetic and vendor-neutral.
- **Why:** Wholesaler transactions are required to reconcile purchased and distributed quantities with rebate claims.
- **Verified:** The user approved `USE_CASE.md` after the wholesaler revision.
