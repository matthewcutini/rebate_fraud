Generated 2026-11-19T20:56:03Z by tools/generate_evidence.py from the live workspace

# Genie Benchmark Comparison

This file proves every benchmark by executing its ground-truth SQL live, asking the deployed governed Genie space, and comparing returned values; entity names and identities are redacted.

## Benchmark Summary

| Space ID | Benchmarks | Matches | Mismatches |
| --- | ---: | ---: | ---: |
| `01f1e3b93f4b11e79b2fbfcd74547821` | 15 | 15 | 0 |

## q01 — MATCH

**Question:** What is the total estimated overpayment exposure by review month?

**Ground-truth statement:** `01f1e45b-a3bb-105d-bde0-c3ea1de1eda7`

| review_period | total_estimated_exposure |
| --- | --- |
| 2025-11 | 893017.84 |
| 2025-12 | 893017.84 |
| 2026-01 | 893017.84 |
| 2026-02 | 893017.84 |
| 2026-03 | 893017.81 |
| 2026-04 | 893017.81 |
| 2026-05 | 893017.81 |
| 2026-06 | 893017.81 |
| 2026-07 | 893017.75 |
| 2026-08 | 893017.75 |
| 2026-10 | 893017.75 |

**Genie SQL**

```sql
SELECT `review_period`, ROUND(SUM(`estimated_overpayment`), 2) AS `total_estimated_exposure` FROM `vandelay`.`rebate_fraud`.`governed_case_features` WHERE `review_period` IS NOT NULL GROUP BY `review_period` ORDER BY `review_period`
```

**Genie result**

| review_period | total_estimated_exposure |
| --- | --- |
| 2025-11 | 893017.84 |
| 2025-12 | 893017.84 |
| 2026-01 | 893017.84 |
| 2026-02 | 893017.84 |
| 2026-03 | 893017.81 |
| 2026-04 | 893017.81 |
| 2026-05 | 893017.81 |
| 2026-06 | 893017.81 |
| 2026-07 | 893017.75 |
| 2026-08 | 893017.75 |
| 2026-10 | 893017.75 |

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.


## q02 — MATCH

**Question:** How many suspected fraud cases exist, and what is their total estimated exposure?

**Ground-truth statement:** `01f1e45b-a3ba-1f1c-b7eb-55a3d18265ab`

| suspected_case_count | total_estimated_exposure |
| --- | --- |
| 21845 | 9823195.85 |

**Genie SQL**

```sql
SELECT COUNT(DISTINCT `case_id`) AS `suspected_case_count`, ROUND(SUM(`estimated_overpayment`), 2) AS `total_estimated_exposure` FROM `vandelay`.`rebate_fraud`.`governed_case_features`
```

**Genie result**

| suspected_case_count | total_estimated_exposure |
| --- | --- |
| 21845 | 9823195.85 |

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.


## q03 — MATCH

**Question:** Which ten pharmacies have the highest estimated overpayment exposure?

**Ground-truth statement:** `01f1e45b-a3a0-1b38-8888-86363115737b`

| pharmacy_id | pharmacy_name | total_estimated_exposure |
| --- | --- | --- |
| REF-000488 | [REDACTED] | 207799.14 |
| REF-000396 | [REDACTED] | 207668.42 |
| REF-000080 | [REDACTED] | 207628.20 |
| REF-000235 | [REDACTED] | 202777.79 |
| REF-000281 | [REDACTED] | 152777.79 |
| REF-000327 | [REDACTED] | 152777.79 |
| REF-000373 | [REDACTED] | 152777.79 |
| REF-000011 | [REDACTED] | 152777.77 |
| REF-000057 | [REDACTED] | 152777.77 |
| REF-000103 | [REDACTED] | 152777.77 |

**Genie SQL**

```sql
WITH pharmacy_exposure AS (   SELECT     governed_case_features.pharmacy_id,     governed_case_features.pharmacy_name,     ROUND(SUM(governed_case_features.estimated_overpayment), 2) AS total_estimated_exposure   FROM vandelay.rebate_fraud.governed_case_features AS governed_case_features   WHERE governed_case_features.pharmacy_id IS NOT NULL     AND governed_case_features.pharmacy_name IS NOT NULL     AND governed_case_features.estimated_overpayment IS NOT NULL   GROUP BY governed_case_features.pharmacy_id, governed_case_features.pharmacy_name ), ranked_pharmacies AS (   SELECT     pharmacy_exposure.pharmacy_id,     pharmacy_exposure.pharmacy_name,     pharmacy_exposure.total_estimated_exposure,     RANK() OVER (       ORDER BY pharmacy_exposure.total_estimated_exposure DESC, pharmacy_exposure.pharmacy_id ASC     ) AS exposure_rank   FROM pharmacy_exposure ) SELECT   ranked_pharmacies.pharmacy_id,   ranked_pharmacies.pharmacy_name,   ranked_pharmacies.total_estimated_exposure FROM ranked_pharmacies WHERE ranked_pharmacies.exposure_rank <= 10 ORDER BY ranked_pharmacies.exposure_rank ASC, ranked_pharmacies.pharmacy_id ASC
```

**Genie result**

| pharmacy_id | pharmacy_name | total_estimated_exposure |
| --- | --- | --- |
| REF-000488 | [REDACTED] | 207799.14 |
| REF-000396 | [REDACTED] | 207668.42 |
| REF-000080 | [REDACTED] | 207628.20 |
| REF-000235 | [REDACTED] | 202777.79 |
| REF-000281 | [REDACTED] | 152777.79 |
| REF-000327 | [REDACTED] | 152777.79 |
| REF-000373 | [REDACTED] | 152777.79 |
| REF-000011 | [REDACTED] | 152777.77 |
| REF-000057 | [REDACTED] | 152777.77 |
| REF-000103 | [REDACTED] | 152777.77 |

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.


## q04 — MATCH

**Question:** How have claimed units, supported units, and excess units changed by month?

**Ground-truth statement:** `01f1e45b-b096-1273-b76f-6f0bbf7dca45`

| review_period | claimed_units | supported_units | excess_units |
| --- | --- | --- | --- |
| 2025-11 | 32693.00 | 569565.00 | 2532.00 |
| 2025-12 | 32992.00 | 566607.00 | 2532.00 |
| 2026-01 | 32443.00 | 566282.00 | 2532.00 |
| 2026-02 | 32542.00 | 563403.00 | 2532.00 |
| 2026-03 | 32728.00 | 566565.00 | 2532.00 |
| 2026-04 | 32977.00 | 567864.00 | 2532.00 |
| 2026-05 | 32975.00 | 569077.00 | 2532.00 |
| 2026-06 | 32819.00 | 565730.00 | 2532.00 |
| 2026-07 | 32707.00 | 565114.00 | 2532.00 |
| 2026-08 | 33044.00 | 566707.00 | 2532.00 |
| 2026-10 | 32913.00 | 570423.00 | 2532.00 |

**Genie SQL**

```sql
SELECT `review_period`, ROUND(SUM(`claimed_units`), 2) AS `claimed_units`, ROUND(SUM(`supported_units`), 2) AS `supported_units`, ROUND(SUM(`excess_units`), 2) AS `excess_units` FROM `vandelay`.`rebate_fraud`.`governed_case_features` WHERE `review_period` IS NOT NULL GROUP BY `review_period` ORDER BY `review_period`
```

**Genie result**

| review_period | claimed_units | supported_units | excess_units |
| --- | --- | --- | --- |
| 2025-11 | 32693.00 | 569565.00 | 2532.00 |
| 2025-12 | 32992.00 | 566607.00 | 2532.00 |
| 2026-01 | 32443.00 | 566282.00 | 2532.00 |
| 2026-02 | 32542.00 | 563403.00 | 2532.00 |
| 2026-03 | 32728.00 | 566565.00 | 2532.00 |
| 2026-04 | 32977.00 | 567864.00 | 2532.00 |
| 2026-05 | 32975.00 | 569077.00 | 2532.00 |
| 2026-06 | 32819.00 | 565730.00 | 2532.00 |
| 2026-07 | 32707.00 | 565114.00 | 2532.00 |
| 2026-08 | 33044.00 | 566707.00 | 2532.00 |
| 2026-10 | 32913.00 | 570423.00 | 2532.00 |

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.


## q05 — MATCH

**Question:** Compare estimated exposure across regions and show each region's share of total exposure.

**Ground-truth statement:** `01f1e45b-b0bb-164c-9238-be81c0aa2ab7`

| region | estimated_exposure | exposure_share_percent |
| --- | --- | --- |
| WEST | 3985320.57 | 40.57 |
| SOUTH | 2645632.92 | 26.93 |
| NORTHEAST | 2088988.00 | 21.27 |
| MIDWEST | 1103254.36 | 11.23 |

**Genie SQL**

```sql
WITH `region_exposure` AS (   SELECT     `region`,     SUM(`estimated_overpayment`) AS `total_estimated_exposure`   FROM `vandelay`.`rebate_fraud`.`governed_case_features`   WHERE `region` IS NOT NULL   GROUP BY `region` ), `grand_total` AS (   SELECT SUM(`total_estimated_exposure`) AS `overall_estimated_exposure`   FROM `region_exposure` ) SELECT   `region_exposure`.`region`,   ROUND(`region_exposure`.`total_estimated_exposure`, 2) AS `total_estimated_exposure`,   100 * (try_divide(`region_exposure`.`total_estimated_exposure`,NULLIF(`grand_total`.`overall_estimated_exposure`, 0))) AS `share_of_total_exposure` FROM `region_exposure` CROSS JOIN `grand_total` ORDER BY `total_estimated_exposure` DESC, `region_exposure`.`region`
```

**Genie result**

| region | total_estimated_exposure | share_of_total_exposure |
| --- | --- | --- |
| WEST | 3985320.57 | 40.570500 |
| SOUTH | 2645632.92 | 26.932500 |
| NORTHEAST | 2088988.00 | 21.265900 |
| MIDWEST | 1103254.36 | 11.231100 |

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.


## q06 — MATCH

**Question:** How much exposure involves cross-channel activity versus single-channel activity?

**Ground-truth statement:** `01f1e45b-b11b-15ef-b813-f4e0c63a48d3`

| activity_type | total_estimated_exposure |
| --- | --- |
| Cross-channel activity | 5555235.05 |
| Single-channel activity | 4267960.79 |

**Genie SQL**

```sql
SELECT CASE WHEN governed_case_features.has_cross_channel_activity = true THEN 'Cross-channel activity' ELSE 'Single-channel activity' END AS activity_type, ROUND(SUM(governed_case_features.estimated_overpayment), 2) AS total_estimated_exposure FROM vandelay.rebate_fraud.governed_case_features AS governed_case_features WHERE governed_case_features.has_cross_channel_activity IS NOT NULL GROUP BY CASE WHEN governed_case_features.has_cross_channel_activity = true THEN 'Cross-channel activity' ELSE 'Single-channel activity' END ORDER BY total_estimated_exposure DESC, activity_type
```

**Genie result**

| activity_type | total_estimated_exposure |
| --- | --- |
| Cross-channel activity | 5555235.05 |
| Single-channel activity | 4267960.79 |

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.


## q07 — MATCH

**Question:** Show the ten case records with the highest estimated overpayment exposure, breaking ties by excess units.

**Ground-truth statement:** `01f1e45b-ba2e-1511-82b6-0f706352555c`

| case_id | pharmacy_name | product_code | review_period | excess_units | estimated_overpayment |
| --- | --- | --- | --- | --- | --- |
| 50375d16e6cdb9bee5d626b3003d73be91afc3c7442f95f4bc596f718835300d | [REDACTED] | 99999-0301-01 | 2025-11 | 495.00 | 152777.79 |
| 50dce036c9dbdb79a9a7cf99c7058309c5dc91996dbad1722e58a5d837021142 | [REDACTED] | 99999-0301-01 | 2026-01 | 495.00 | 152777.79 |
| 9b47147353c3e4fd0e1cf3908b99d2b8b593c280d7d7132388a47e81377f0ecd | [REDACTED] | 99999-0102-01 | 2025-12 | 495.00 | 152777.79 |
| cd6705dddbaa2aead8d8aae93791d84adc26d9fc2a5ca8f5483d3c256402407a | [REDACTED] | 99999-0102-01 | 2026-02 | 495.00 | 152777.79 |
| 0b17368ac8b483e680b26da562e0ed2a1b14c82c13beb5edb23ec0e36df61877 | [REDACTED] | 99999-0301-01 | 2026-07 | 495.00 | 152777.77 |
| 31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64 | [REDACTED] | 99999-0102-01 | 2026-10 | 495.00 | 152777.77 |
| 3b7ba9fd5175ee3bb5cd1e61e632775417cb128c762a234201f66d7f4a8ea9f3 | [REDACTED] | 99999-0301-01 | 2026-03 | 495.00 | 152777.77 |
| 46db4cb8b07bb599325af9b59c954e800e9f7261fbc6aca6bb1bc003e71376ed | [REDACTED] | 99999-0301-01 | 2026-05 | 495.00 | 152777.77 |
| 56801fee4f5645973398022792b2e071f4f96380e0177a682a1816fcfc97faa1 | [REDACTED] | 99999-0102-01 | 2026-08 | 495.00 | 152777.77 |
| 77039103eb6625099e758d12b1e248d2a8b6f5d5deffc2534191156fcc88d014 | [REDACTED] | 99999-0102-01 | 2026-06 | 495.00 | 152777.77 |

**Genie SQL**

```sql
SELECT `case_id`, `pharmacy_id`, `pharmacy_name`, `product_code`, `review_period`, `excess_units`, ROUND(`estimated_overpayment`, 2) AS `estimated_overpayment` FROM `vandelay`.`rebate_fraud`.`governed_case_features` WHERE `estimated_overpayment` IS NOT NULL   AND `excess_units` IS NOT NULL ORDER BY `estimated_overpayment` DESC, `excess_units` DESC, `case_id` ASC LIMIT 10
```

**Genie result**

| case_id | pharmacy_id | pharmacy_name | product_code | review_period | excess_units | estimated_overpayment |
| --- | --- | --- | --- | --- | --- | --- |
| 50375d16e6cdb9bee5d626b3003d73be91afc3c7442f95f4bc596f718835300d | REF-000235 | [REDACTED] | 99999-0301-01 | 2025-11 | 495.00 | 152777.79 |
| 50dce036c9dbdb79a9a7cf99c7058309c5dc91996dbad1722e58a5d837021142 | REF-000327 | [REDACTED] | 99999-0301-01 | 2026-01 | 495.00 | 152777.79 |
| 9b47147353c3e4fd0e1cf3908b99d2b8b593c280d7d7132388a47e81377f0ecd | REF-000281 | [REDACTED] | 99999-0102-01 | 2025-12 | 495.00 | 152777.79 |
| cd6705dddbaa2aead8d8aae93791d84adc26d9fc2a5ca8f5483d3c256402407a | REF-000373 | [REDACTED] | 99999-0102-01 | 2026-02 | 495.00 | 152777.79 |
| 0b17368ac8b483e680b26da562e0ed2a1b14c82c13beb5edb23ec0e36df61877 | REF-000103 | [REDACTED] | 99999-0301-01 | 2026-07 | 495.00 | 152777.77 |
| 31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64 | REF-000241 | [REDACTED] | 99999-0102-01 | 2026-10 | 495.00 | 152777.77 |
| 3b7ba9fd5175ee3bb5cd1e61e632775417cb128c762a234201f66d7f4a8ea9f3 | REF-000419 | [REDACTED] | 99999-0301-01 | 2026-03 | 495.00 | 152777.77 |
| 46db4cb8b07bb599325af9b59c954e800e9f7261fbc6aca6bb1bc003e71376ed | REF-000011 | [REDACTED] | 99999-0301-01 | 2026-05 | 495.00 | 152777.77 |
| 56801fee4f5645973398022792b2e071f4f96380e0177a682a1816fcfc97faa1 | REF-000149 | [REDACTED] | 99999-0102-01 | 2026-08 | 495.00 | 152777.77 |
| 77039103eb6625099e758d12b1e248d2a8b6f5d5deffc2534191156fcc88d014 | REF-000057 | [REDACTED] | 99999-0102-01 | 2026-06 | 495.00 | 152777.77 |

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.


## q08 — MATCH

**Question:** For case 31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64, show its quantities, channel evidence, identity evidence, entity status, and estimated exposure.

**Ground-truth statement:** `01f1e45b-bde2-13e2-af7c-2cfa7874c52e`

| case_id | pharmacy_name | entity_status | product_code | review_period | claimed_units | supported_units | excess_units | manufacturer_units | wholesaler_units | has_cross_channel_activity | matched_cross_channel_pairs | has_multiple_source_identities | source_identity_count | estimated_overpayment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64 | [REDACTED] | ACTIVE | 99999-0102-01 | 2026-10 | 540.00 | 45.00 | 495.00 | 45.00 | 0.00 | true | 1 | false | 1 | 152777.77 |

**Genie SQL**

```sql
SELECT `case_id`, `pharmacy_id`, `pharmacy_name`, `product_code`, `review_period`, `claimed_units`, `manufacturer_units`, `wholesaler_units`, `supported_units`, `excess_units`, `claim_count`, `medical_claim_count`, `pharmacy_claim_count`, `channel_count`, `has_cross_channel_activity`, `matched_cross_channel_pairs`, `source_identity_count`, `has_multiple_source_identities`, `entity_status`, ROUND(`estimated_overpayment`, 2) AS `estimated_overpayment` FROM `vandelay`.`rebate_fraud`.`governed_case_features` WHERE `case_id` = '31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64' LIMIT 1
```

**Genie result**

| case_id | pharmacy_id | pharmacy_name | product_code | review_period | claimed_units | manufacturer_units | wholesaler_units | supported_units | excess_units | claim_count | medical_claim_count | pharmacy_claim_count | channel_count | has_cross_channel_activity | matched_cross_channel_pairs | source_identity_count | has_multiple_source_identities | entity_status | estimated_overpayment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64 | REF-000241 | [REDACTED] | 99999-0102-01 | 2026-10 | 540.00 | 45.00 | 0.00 | 45.00 | 495.00 | 2 | 1 | 1 | 2 | true | 1 | 1 | false | ACTIVE | 152777.77 |

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.


## q09 — MATCH

**Question:** How many cases involve multiple source identities, and how does their average estimated exposure compare with other cases?

**Ground-truth statement:** `01f1e45b-bde8-1d51-a291-5d022d6f0ced`

| case_group | case_count | avg_estimated_exposure |
| --- | --- | --- |
| Other cases | 19686 | 493.91 |
| Multiple source identities | 2159 | 46.32 |

**Genie SQL**

```sql
SELECT CASE WHEN governed_case_features.has_multiple_source_identities = true THEN 'Multiple source identities' ELSE 'Other cases' END AS case_group, COUNT(DISTINCT governed_case_features.case_id) AS case_count, ROUND(AVG(governed_case_features.estimated_overpayment), 2) AS avg_estimated_exposure FROM vandelay.rebate_fraud.governed_case_features AS governed_case_features WHERE governed_case_features.case_id IS NOT NULL GROUP BY CASE WHEN governed_case_features.has_multiple_source_identities = true THEN 'Multiple source identities' ELSE 'Other cases' END ORDER BY avg_estimated_exposure DESC, case_group
```

**Genie result**

| case_group | case_count | avg_estimated_exposure |
| --- | --- | --- |
| Other cases | 19686 | 493.91 |
| Multiple source identities | 2159 | 46.32 |

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.


## q10 — MATCH

**Question:** Compare suspected cases for active, pending, and closed pharmacy entities.

**Ground-truth statement:** `01f1e45b-c6f8-1525-8fe3-45b20ca41e87`

| entity_status | suspected_case_count |
| --- | --- |
| ACTIVE | 20973 |
| CLOSED | 872 |

**Genie SQL**

```sql
SELECT   `entity_status`,   COUNT(DISTINCT `case_id`) AS `suspected_case_count` FROM `vandelay`.`rebate_fraud`.`governed_case_features` WHERE `entity_status` IS NOT NULL   AND (     `entity_status` ILIKE '%ACTIVE%'     OR `entity_status` ILIKE '%PENDING%'     OR `entity_status` ILIKE '%CLOSED%'   ) GROUP BY `entity_status` ORDER BY `suspected_case_count` DESC, `entity_status`
```

**Genie result**

| entity_status | suspected_case_count |
| --- | --- |
| ACTIVE | 20973 |
| CLOSED | 872 |

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.


## q11 — MATCH

**Question:** By month, how many pharmacy and product combinations have claimed units greater than supported units?

**Ground-truth statement:** `01f1e45b-ca85-1ad6-8ae8-9d2049f15fa9`

| review_period | excess_claim_combinations |
| --- | --- |
| 2025-11 | 13 |
| 2025-12 | 13 |
| 2026-01 | 13 |
| 2026-02 | 13 |
| 2026-03 | 13 |
| 2026-04 | 13 |
| 2026-05 | 13 |
| 2026-06 | 13 |
| 2026-07 | 13 |
| 2026-08 | 13 |
| 2026-10 | 13 |

**Genie SQL**

```sql
SELECT   `review_period`,   COUNT(DISTINCT CONCAT_WS('||', `pharmacy_id`, `product_code`)) AS `pharmacy_product_combination_count` FROM `vandelay`.`rebate_fraud`.`governed_case_features` WHERE `review_period` IS NOT NULL   AND `claimed_units` > `supported_units` GROUP BY `review_period` ORDER BY `review_period`
```

**Genie result**

| review_period | pharmacy_product_combination_count |
| --- | --- |
| 2025-11 | 13 |
| 2025-12 | 13 |
| 2026-01 | 13 |
| 2026-02 | 13 |
| 2026-03 | 13 |
| 2026-04 | 13 |
| 2026-05 | 13 |
| 2026-06 | 13 |
| 2026-07 | 13 |
| 2026-08 | 13 |
| 2026-10 | 13 |

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.


## q12 — MATCH

**Question:** Which cases combine excess claimed units, cross-channel activity, and multiple source identities?

**Ground-truth statement:** `01f1e45b-cafb-1f9e-a78d-4e0ca4f7658c`

| case_id | pharmacy_name | product_code | review_period | excess_units | estimated_overpayment |
| --- | --- | --- | --- | --- | --- |
| 5ca92443ba6a6b87bd3dfd72715aa4c530ba2cdc4dae4235ae3c9b375ad1c12a | [REDACTED] | 99999-0301-01 | 2026-06 | 20.00 | 50000.00 |
| 617c03c477d1fa9d29e87f75ee334eaa52792f086725f8870ad6bb3ee18a92f0 | [REDACTED] | 99999-0101-01 | 2025-12 | 21.00 | 50000.00 |

**Genie SQL**

```sql
SELECT governed_case_features.case_id, governed_case_features.pharmacy_id, governed_case_features.pharmacy_name, governed_case_features.product_code, governed_case_features.review_period, governed_case_features.claimed_units, governed_case_features.supported_units, governed_case_features.excess_units, ROUND(governed_case_features.estimated_overpayment, 2) AS estimated_overpayment, governed_case_features.matched_cross_channel_pairs, governed_case_features.source_identity_count FROM vandelay.rebate_fraud.governed_case_features AS governed_case_features WHERE governed_case_features.excess_units > 0   AND governed_case_features.has_cross_channel_activity = TRUE   AND governed_case_features.has_multiple_source_identities = TRUE   AND governed_case_features.case_id IS NOT NULL   AND governed_case_features.estimated_overpayment IS NOT NULL ORDER BY governed_case_features.estimated_overpayment DESC, governed_case_features.case_id
```

**Genie result**

| case_id | pharmacy_id | pharmacy_name | product_code | review_period | claimed_units | supported_units | excess_units | estimated_overpayment | matched_cross_channel_pairs | source_identity_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5ca92443ba6a6b87bd3dfd72715aa4c530ba2cdc4dae4235ae3c9b375ad1c12a | REF-000172 | [REDACTED] | 99999-0301-01 | 2026-06 | 40.00 | 20.00 | 20.00 | 50000.00 | 1 | 2 |
| 617c03c477d1fa9d29e87f75ee334eaa52792f086725f8870ad6bb3ee18a92f0 | REF-000235 | [REDACTED] | 99999-0101-01 | 2025-12 | 42.00 | 21.00 | 21.00 | 50000.00 | 1 | 2 |

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.


## q13 — MATCH

**Question:** How many case records are missing pharmacy ID, pharmacy name, region, or state code?

**Ground-truth statement:** `01f1e45b-d09e-1f8b-b30d-93ad7d337c6b`

| missing_case_record_count |
| --- |
| 0 |

**Genie SQL**

```sql
SELECT COUNT(*) AS missing_any_count, COUNT_IF(`pharmacy_id` IS NULL) AS missing_pharmacy_id_count, COUNT_IF(`pharmacy_name` IS NULL) AS missing_pharmacy_name_count, COUNT_IF(`region` IS NULL) AS missing_region_count, COUNT_IF(`state_code` IS NULL) AS missing_state_code_count FROM `vandelay`.`rebate_fraud`.`governed_case_features` WHERE `pharmacy_id` IS NULL OR `pharmacy_name` IS NULL OR `region` IS NULL OR `state_code` IS NULL
```

**Genie result**

| missing_any_count | missing_pharmacy_id_count | missing_pharmacy_name_count | missing_region_count | missing_state_code_count |
| --- | --- | --- | --- | --- |
| 0 | 0 | 0 | 0 | 0 |

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.


## q14 — MATCH

**Question:** How many case records are missing claimed units, supported units, excess units, or estimated exposure?

**Ground-truth statement:** `01f1e45b-d3be-1f0d-97f5-a0547d437d3e`

| missing_claimed_units | missing_supported_units | missing_excess_units | missing_estimated_exposure |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 0 |

**Genie SQL**

```sql
SELECT   COUNT_IF(`claimed_units` IS NULL) AS `missing_claimed_units`,   COUNT_IF(`supported_units` IS NULL) AS `missing_supported_units`,   COUNT_IF(`excess_units` IS NULL) AS `missing_excess_units`,   COUNT_IF(`estimated_overpayment` IS NULL) AS `missing_estimated_exposure` FROM `vandelay`.`rebate_fraud`.`governed_case_features`
```

**Genie result**

| missing_claimed_units | missing_supported_units | missing_excess_units | missing_estimated_exposure |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 0 |

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.


## q15 — MATCH

**Question:** For each product, compare total claimed units, manufacturer units, wholesaler units, supported units, and excess units.

**Ground-truth statement:** `01f1e45b-d86b-12b6-95df-76d8c8024bee`

| product_code | claimed_units | manufacturer_units | wholesaler_units | supported_units | excess_units |
| --- | --- | --- | --- | --- | --- |
| 99999-0101-01 | 90413.00 | 649951.00 | 904399.00 | 1554350.00 | 7101.00 |
| 99999-0102-01 | 90003.00 | 650604.00 | 903638.00 | 1554242.00 | 7408.00 |
| 99999-0201-01 | 90093.00 | 658156.00 | 901944.00 | 1560100.00 | 6620.00 |
| 99999-0301-01 | 90324.00 | 656381.00 | 912264.00 | 1568645.00 | 6723.00 |

**Genie SQL**

```sql
SELECT `product_code`, SUM(`claimed_units`) AS `total_claimed_units`, SUM(`manufacturer_units`) AS `total_manufacturer_units`, SUM(`wholesaler_units`) AS `total_wholesaler_units`, SUM(`supported_units`) AS `total_supported_units`, SUM(`excess_units`) AS `total_excess_units` FROM `vandelay`.`rebate_fraud`.`governed_case_features` WHERE `product_code` IS NOT NULL GROUP BY `product_code` ORDER BY `product_code`
```

**Genie result**

| product_code | total_claimed_units | total_manufacturer_units | total_wholesaler_units | total_supported_units | total_excess_units |
| --- | --- | --- | --- | --- | --- |
| 99999-0101-01 | 90413.00 | 649951.00 | 904399.00 | 1554350.00 | 7101.00 |
| 99999-0102-01 | 90003.00 | 650604.00 | 903638.00 | 1554242.00 | 7408.00 |
| 99999-0201-01 | 90093.00 | 658156.00 | 901944.00 | 1560100.00 | 6620.00 |
| 99999-0301-01 | 90324.00 | 656381.00 | 912264.00 | 1568645.00 | 6723.00 |

**Genie answer:** The structured live result is shown above. Free-form prose is intentionally omitted because it can repeat synthetic entity names.
