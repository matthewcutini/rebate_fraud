Generated 2026-11-19T20:24:45Z by tools/generate_evidence.py from the live workspace

# Data Quality and Completeness

This file proves rejected records remain explainable, every released period reconciles to its manifest, and required business keys and exposure fields are complete in live gold data.

## Quarantine Reasons

Statement `01f1e457-440b-1437-8ec0-0574883d0e5a`:

| quarantine_reason | rows |
| --- | --- |
| EXACT_RETRANSMISSION | 110 |
| INVALID_SERVICE_DATE | 22 |
| MISSING_CLAIM_ID | 33 |
| NON_POSITIVE_REBATE_UNITS | 22 |
| UNKNOWN_PRODUCT_CODE | 22 |

## Period Reconciliation

Statement `01f1e457-4498-18fc-89c1-9810c51aef63`:

| period | expected_claim_rows | landed_claim_rows | loaded_claim_rows | quarantined_claim_rows | reconciliation_status | claim_amount_difference |
| --- | --- | --- | --- | --- | --- | --- |
| 2025-11 | 10000 | 10000 | 9981 | 19 | RECONCILED | 0.00 |
| 2025-12 | 10000 | 10000 | 9981 | 19 | RECONCILED | 0.00 |
| 2026-01 | 10000 | 10000 | 9981 | 19 | RECONCILED | 0.00 |
| 2026-02 | 10000 | 10000 | 9981 | 19 | RECONCILED | 0.00 |
| 2026-03 | 10000 | 10000 | 9981 | 19 | RECONCILED | 0.00 |
| 2026-04 | 10000 | 10000 | 9981 | 19 | RECONCILED | 0.00 |
| 2026-05 | 10000 | 10000 | 9981 | 19 | RECONCILED | 0.00 |
| 2026-06 | 10000 | 10000 | 9981 | 19 | RECONCILED | 0.00 |
| 2026-07 | 10000 | 10000 | 9981 | 19 | RECONCILED | 0.00 |
| 2026-08 | 10000 | 10000 | 9981 | 19 | RECONCILED | 0.00 |
| 2026-10 | 10000 | 10000 | 9981 | 19 | RECONCILED | 0.00 |

## Gold Completeness

Statement `01f1e457-4560-1933-a97f-3432b9775e1c`:

| gold_rows | missing_case_id | missing_pharmacy_id | missing_product_code | missing_review_period | missing_exposure |
| --- | --- | --- | --- | --- | --- |
| 21845 | 0 | 0 | 0 | 0 | 0 |
