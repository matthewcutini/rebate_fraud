Generated 2026-11-19T20:23:34Z by tools/generate_evidence.py from the live workspace

# Lakeflow Pipeline Run

This file proves the deployed serverless pipeline completed and reports live bronze, silver, quarantine, reconciliation, and gold row counts plus its expectation payloads.

## Live Pipeline

| Pipeline ID | Name | Latest completed update | State | Serverless | Catalog | Schema |
| --- | --- | --- | --- | --- | --- | --- |
| `83a6f0b6-694b-49eb-b0df-c95648e18f3e` | `[dev matt_cutini] rebate-fraud-pipeline` | `ca39b633-0fbc-481d-abce-a074371b5f35` | `COMPLETED` | `True` | `vandelay` | `rebate_fraud` |

- Update start: ``
- Update end: ``
- Final orchestration run: `806236758003209`

## Live Row Counts

Statement `01f1e457-19d9-192c-a78d-a2bde55b1895`:

| table_name | row_count |
| --- | --- |
| bronze_control_manifest | 11 |
| bronze_manufacturer_sales | 137500 |
| bronze_medical_claims | 49500 |
| bronze_pharmacy_claims | 60500 |
| bronze_wholesaler_shipments | 229167 |
| gold_case_features | 21845 |
| quarantine_claims | 209 |
| reconciliation_claims | 11 |
| silver_claims | 109791 |
| silver_claims_conformed | 109901 |
| silver_pharmacy_entities | 500 |
| silver_product_movement | 366667 |

## Latest Update Expectation Payloads

Statement `01f1e457-1c19-187b-99cd-e2140d33fc8b`:

| update_id | expectation_metrics |
| --- | --- |
| ca39b633-0fbc-481d-abce-a074371b5f35 | [{"name":"claims_reconciled","dataset":"vandelay.rebate_fraud.reconciliation_claims","passed_records":11,"failed_records":0}] |
