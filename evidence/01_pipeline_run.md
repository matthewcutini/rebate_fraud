# Lakeflow Pipeline Run Evidence

## Deployed Resource

- Pipeline ID: `83a6f0b6-694b-49eb-b0df-c95648e18f3e`
- Catalog and schema: `vandelay.rebate_fraud`
- Compute: serverless, Photon enabled
- Landing path: `/Volumes/vandelay/rebate_fraud/landing/ready`
- Successful initial data update: `2fcaf4bd-0e49-4fd9-afcc-19dfe6d3200d`
- Final deployed update after gold-feature refinement: `60a2cdad-c07d-4bbb-a6e0-eefd65eb58b4`
- Final state: `COMPLETED`
- Final update duration: 31 seconds (`2026-11-18T16:39:18.699Z` through `2026-11-18T16:39:49.947Z`)

The deployed resource was read back with `databricks pipelines get`. It reports `serverless: true`, catalog `vandelay`, target `rebate_fraud`, and all four SQL libraries.

## Row Counts

| Table | Rows |
|---|---:|
| `bronze_control_manifest` | 10 |
| `bronze_manufacturer_sales` | 125,000 |
| `bronze_medical_claims` | 45,000 |
| `bronze_pharmacy_claims` | 55,000 |
| `bronze_pharmacy_reference` | 5,000 |
| `bronze_wholesaler_shipments` | 208,334 |
| `silver_claims_conformed` | 99,910 |
| `silver_claims` | 99,810 |
| `quarantine_claims` | 190 |
| `silver_product_movement` | 333,334 |
| `silver_pharmacy_entities` | 500 |
| `reconciliation_claims` | 10 |
| `gold_case_features` | 19,881 |

## Quarantine Results

| Reason | Rows |
|---|---:|
| `EXACT_RETRANSMISSION` | 100 |
| `INVALID_SERVICE_DATE` | 20 |
| `MISSING_CLAIM_ID` | 30 |
| `NON_POSITIVE_REBATE_UNITS` | 20 |
| `UNKNOWN_PRODUCT_CODE` | 20 |
| **Total** | **190** |

These are the expected counts for the 10 released periods. Two holdback periods remain outside the pipeline landing path for the live-arrival demonstration.

Example retained record:

```text
channel=MEDICAL
claim_id=MC202511004488
product_code=99999-0101-01
service_date_raw=2025-11-19
rebate_units_raw=5
quarantine_reason=EXACT_RETRANSMISSION
source_period=2025-11
```

## Reconciliation

All 10 released periods returned `RECONCILED`.

```text
periods=10
expected rows per period=10,000
landed rows per period=10,000
loaded rows per period=9,981
quarantined rows per period=19
loaded + quarantined=10,000
claim amount differences=0.00
BREAK periods=0
```

## Expectation Metrics

Metrics below were read from `event_log('83a6f0b6-694b-49eb-b0df-c95648e18f3e')` for successful initial data update `2fcaf4bd-0e49-4fd9-afcc-19dfe6d3200d`.

| Expectation | Passed | Failed | Action |
|---|---:|---:|---|
| `compatible_medical_schema` | 45,000 | 0 | Fail update |
| `compatible_pharmacy_schema` | 55,000 | 0 | Fail update |
| `compatible_sales_schema` | 125,000 | 0 | Fail update |
| `compatible_wholesaler_schema` | 208,334 | 0 | Fail update |
| `compatible_reference_schema` | 5,000 | 0 | Fail update |
| `compatible_manifest_schema` | 10 | 0 | Fail update |
| `claim_id_present` | 99,970 | 30 | Drop and quarantine |
| `positive_rebate_units` | 99,980 | 20 | Drop and quarantine |
| `valid_service_date` | 99,980 | 20 | Drop and quarantine |
| `known_product_code` | 99,980 | 20 | Drop and quarantine |
| `timely_claim` | 99,780 | 220 | Warn and retain |
| `clean_pharmacy_name` | 99,500 | 500 | Warn and clean |
| `contact_available` | 99,750 | 250 | Warn and retain |
| `claims_reconciled` | 10 | 0 | Fail update |

The two claim flows reported 90 dropped rows and 950 warning evaluations. Exact retransmissions are removed in the deterministic silver materialized view and retained separately in quarantine.

## Gold Sanity Check

```text
gold_feature_rows=19,881
excess_quantity_groups=150
matched_high_value_cross_channel_groups=60
multi_name_groups=1,970
estimated_overpayment=8,937,679.04
```

The 60 matched cross-channel groups equal the 72 annual planted cross-channel and combined cases scaled to the 10 released months; the remaining 12 are in the two holdback periods.

## Idempotency

Update `71bc8eef-c9d3-4f67-83dd-c7f35ec4264a` completed with no new files. Counts after the rerun remained:

```text
bronze_medical=45,000
bronze_pharmacy=55,000
silver_conformed=99,910
silver_deduped=99,810
quarantined=190
gold_features=19,881
```

No rows were duplicated by the second run.

## Failed Attempt Preserved

Update `d9f86cee-4c80-4931-b8ff-b232cd19c37d` failed during setup because multiplying the wholesaler sign by `DECIMAL(18,2)` widened the inferred result to `DECIMAL(29,2)`. The expression result was explicitly cast back to `DECIMAL(18,2)`, redeployed, and the next update completed.
