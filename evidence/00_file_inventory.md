# Synthetic Source File Inventory

**Deployed volume:** `vandelay.rebate_fraud.landing`  
**Verified job run:** `716333328535686`  
**Job result:** `TERMINATED SUCCESS`  
**Generator verification:** `PASS`

## Period Inventory

| State | Period | Files | Bytes |
|---|---|---:|---:|
| ready | 2025-11 | 6 | 7,790,597 |
| ready | 2025-12 | 6 | 7,789,511 |
| ready | 2026-01 | 6 | 7,790,035 |
| ready | 2026-02 | 6 | 7,789,281 |
| ready | 2026-03 | 6 | 7,790,392 |
| ready | 2026-04 | 6 | 7,791,881 |
| ready | 2026-05 | 6 | 7,791,324 |
| ready | 2026-06 | 6 | 7,790,140 |
| ready | 2026-07 | 6 | 7,790,208 |
| ready | 2026-08 | 6 | 7,789,944 |
| holdback | 2026-09 | 6 | 7,790,847 |
| holdback | 2026-10 | 6 | 7,789,690 |

Each period has five source exports and one manifest written last.

## Folder Totals

| Folder | Files | Bytes |
|---|---:|---:|
| `medical_claims` | 12 | 21,141,386 |
| `pharmacy_claims` | 12 | 11,577,716 |
| `manufacturer_sales` | 12 | 21,219,171 |
| `wholesaler_distribution` | 12 | 37,827,253 |
| `pharmacy_reference` | 12 | 1,695,302 |
| `manifest` | 12 | 23,022 |
| **Total** | **72** | **93,483,850** |

## Verification Summary

```json
{
  "alias_pharmacies": 60,
  "bad_product_codes": 24,
  "combined_repeat_offender_cases": 24,
  "cross_channel_only_cases": 48,
  "cross_channel_pairs": 72,
  "duplicate_rows": 120,
  "excess_quantity_cases": 84,
  "file_count": 72,
  "fraud_exposure_dollars": 10000000,
  "holdback_periods": 2,
  "invalid_dates": 24,
  "late_records": 240,
  "missing_claim_ids": 36,
  "missing_contacts": 300,
  "nonpositive_quantities": 24,
  "periods": 12,
  "ready_periods": 10,
  "status": "PASS",
  "total_claim_rows": 120000,
  "trailing_names": 600
}
```

## Deployed File Samples

### Medical Claims JSON Lines

```json
{"billingEntityName":"Meadow 0102 Health Pharmacy","billingNpi":"8000000102","entityAddress":"807 Summit Street, Demo City 29, IL 80101","entityFax":"232-555-0201","entityPhone":"232-555-0101","medClaimId":"MC202511000001","productCode":"99999-0102-01","rebateAmount":"50000.00","rebateUnitsRequested":18,"receivedTimestamp":"2025-11-13T16:20:00Z","serviceFromDate":"2025-11-13","unitsBilled":18}
```

### Pharmacy Claims CSV

```csv
RX_CLAIM_NBR,PHARMACY_NAME,NCPDP_ID,FILL_DATE,PRODUCT_NDC,QTY_DISPENSED,REBATE_UNITS,REBATE_AMT,STORE_ADDR,PHONE_NBR,FAX_NBR,SUBMISSION_TS
RX202511000001,Willow 0012 Care Pharmacy,7000012,2025-11-05,99999-0101-01,240,240,66666.67,"177 Summit Street, Demo City 12, PA 80011",212-555-0111,212-555-0211,2025-11-05T18:15:00Z
```

### Manufacturer Sales CSV

```csv
SALES_DOC_NBR,SOLD_TO_ACCT,SHIP_TO_NAME,SHIP_TO_ADDR,MATERIAL_CD,QTY_SHIPPED,NET_AMT,SHIP_DT,DOC_TYPE
SD2025110000001,S0000012,Willow 0012 Care Pharmacy,"177 Summit Street, Demo City 12, PA 80011",CGM-SENSOR-01,40,7600.00,2025-11-05,SHIPMENT
```

### Wholesaler Distribution PSV

```text
Transaction_ID|Wholesaler_Customer_ID|Customer_Name|Customer_Address|Customer_Phone|Customer_Fax|NDC|Transaction_Type|Quantity|Invoice_Date
WT2025110000001|W0000117|Lumen 0117 Family Pharmacy|912 Cedar Way, Demo City 44, GA 80116|247-555-0116|247-555-0216|99999-0201-01|SALE|7|11/07/2025
```

### Pharmacy Reference JSON Lines

```json
{"address":"100 Aster Loop, Demo City 01, AZ 80000","closedDate":null,"doingBusinessAs":"Aster 0001 Care Pharmacy","effectiveDate":"2020-01-01","fax":"201-555-0200","legalName":"Aster 0001 Care Pharmacy","phone":"201-555-0100","sourceEntityId":"REF-000001","status":"ACTIVE"}
```

### Period Manifest JSON

```json
{
  "period": "2025-11",
  "deliveryState": "ready",
  "controlTotals": {
    "fileCount": 5,
    "recordCount": 43834,
    "claimRecordCount": 10000,
    "claimAmountTotal": "4560280.05"
  }
}
```

## Read-Back Checks

- `databricks volumes read vandelay.rebate_fraud.landing --profile vandelay` confirmed a managed volume in the expected catalog and schema.
- `databricks fs ls` confirmed 10 ready periods and 2 holdback periods.
- Per-folder `databricks fs ls -l` and manifest reads produced the counts and sizes above.
- The generator reread the deployed files and matched every planted count in `evidence/00_answer_key.md`.
