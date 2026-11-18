# Synthetic Rebate Fraud Answer Key

The raw files contain invented organizations, products, identifiers, addresses, phone numbers, and fax numbers. No real customer or person data is used.

## Delivery Layout

- Volume: `vandelay.rebate_fraud.landing`
- Ready periods: `2025-11` through `2026-08`
- Demo holdback periods: `2026-09` and `2026-10`
- Every period contains medical claims, pharmacy claims, manufacturer sales, wholesaler distribution, a pharmacy reference snapshot, and a manifest written last.
- Expected annual claim volume: 120,000 rows, or 10,000 rows per month.

## Planted Fraud Findings

| Finding | Expected count | Expected exposure | Recognition rule |
|---|---:|---:|---|
| Excess-quantity rebate cases | 84 | $5,600,000 | For the resolved pharmacy, product, and month, requested rebate units exceed net manufacturer and wholesaler-supported units. |
| Cross-channel duplicate cases | 48 pairs | $2,400,000 | A medical claim and pharmacy claim resolve to the same entity and have the same product, service date, and units. Supported units cover one claim, not both. |
| Combined repeat-offender cases | 24 | $2,000,000 | The entity appears under alias-style names in both channels, the claims duplicate each other, and requested units exceed supported units. |
| Total fraud exposure | 156 cases | $10,000,000 | Sum the mutually exclusive categories above; count a duplicate pair as one fraud case. |
| Benign identity aliases | 36 pharmacies | $0 | Different source identifiers or name styles resolve through normalized address, phone, or fax, but quantities reconcile and no cross-channel duplicate exists. |
| Hero case | 1 of the 24 combined cases | Included above | Trace one repeat offender through an alias, both claim channels, excess units, later-period activity, and eventual closure status. |

The generator selects cases with fixed hashes and a fixed seed. Counts, identifiers, periods, and dollar allocations remain stable on every rerun.

## Planted Data-Quality Findings

| Finding | Expected count | Recognition rule |
|---|---:|---|
| Exact retransmitted claim rows | 120 | Full-row duplicate within the same source file; 10 per month. |
| Missing claim identifiers | 36 | Empty `medClaimId` or `RX_CLAIM_NBR`; 3 per month. |
| Non-positive requested quantities | 24 | `rebateUnitsRequested <= 0` or `REBATE_UNITS <= 0`; 2 per month. |
| Invalid service dates | 24 | Date cannot be parsed; 2 per month. |
| Unknown product codes | 24 | Product begins `BAD-CODE-`; 2 per month. |
| Late records | 240 | Service or fill month precedes the delivery folder month; 20 per month. |
| Trailing spaces | 600 | Pharmacy name ends with a space; 50 per month. |
| Missing contact values | 300 | Phone or fax is empty; 25 per month. |
| Pharmacy openings | 20 | Reference effective date falls during the generated horizon. |
| Pharmacy closures | 20 | Reference status becomes `CLOSED` during the generated horizon. |

## Entity Resolution Clues

- Medical and pharmacy systems use different claim IDs and entity IDs.
- Manufacturer sales use `SOLD_TO_ACCT`; wholesalers use `Wholesaler_Customer_ID`.
- Medical names use an abbreviated `PHCY` style; pharmacy claims use a DBA-style name.
- Sixty pharmacies have multiple source identity representations: 24 fraudulent combined cases and 36 benign aliases.
- Normalize punctuation, whitespace, casing, phone, fax, and address before comparing records.

## Control Checks

Each `manifest/control_YYYYMM.json` contains file record counts, quantity totals, amount totals, byte sizes, and SHA-256 hashes. The generator reads the written files back and fails unless all planted counts match this answer key.
