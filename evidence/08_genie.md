# Genie Agent Evidence

## Deployed Space

- **Title:** Rebate Fraud Executive Analytics
- **Space ID:** `01f1e3b93f4b11e79b2fbfcd74547821`
- **Workspace profile:** `vandelay`
- **Warehouse ID:** `5d942ad88a289cf7`
- **Governed source:** `vandelay.rebate_fraud.governed_case_features`
- **Result:** 15/15 Conversation API benchmark answers matched the checked SQL results.
- **Comparison:** Expected columns must match by name when possible; otherwise row values are compared independent of harmless aliases, capitalization, and extra explanatory columns. Numbers are compared to two decimals.

## Benchmark Results

### Q01 — MATCH

**Question:** What is the total estimated overpayment exposure by review month?

**Ground-truth result**

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
SELECT `governed_case_features`.`review_period`, ROUND(SUM(`governed_case_features`.`estimated_overpayment`), 2) AS `total_estimated_exposure`
FROM `vandelay`.`rebate_fraud`.`governed_case_features` AS `governed_case_features`
WHERE `governed_case_features`.`review_period` IS NOT NULL
GROUP BY `governed_case_features`.`review_period`
ORDER BY `governed_case_features`.`review_period`
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

**Genie answer:** Across the **11 review months shown** from **2025-11 to 2026-10**, total estimated overpayment exposure stays very consistent at about **$893,017.75 to $893,017.84** per month. Examples include: - **2025-11:** **$893,017.84** - **2025-12:** **$893,017.84** - **2026-03:** **$893,017.81** - **2026-07:** **$893,017.75** - **2026-10:** **$893,017.75** The monthly totals are essentially flat over the available review periods, with only a **$0.09** spread between the highest and lowest months.

**Value match:** Yes

### Q02 — MATCH

**Question:** How many suspected fraud cases exist, and what is their total estimated exposure?

**Ground-truth result**

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

**Genie answer:** There are **21,845** suspected fraud cases, with a total estimated exposure of **$9,823,195.85**. Based on the single result returned, the full count of cases in `governed_case_features` sums to **$9.82 million** in estimated exposure.

**Value match:** Yes

### Q03 — MATCH

**Question:** Which ten pharmacies have the highest estimated overpayment exposure?

**Ground-truth result**

| pharmacy_id | pharmacy_name | total_estimated_exposure |
| --- | --- | --- |
| REF-000488 | Pioneer 0488 Health Pharmacy | 207799.14 |
| REF-000396 | Willow 0396 Care Pharmacy | 207668.42 |
| REF-000080 | Elm 0080 Care Pharmacy | 207628.20 |
| REF-000235 | Timber 0235 Health Pharmacy | 202777.79 |
| REF-000281 | Quartz 0281 Community Pharmacy | 152777.79 |
| REF-000327 | Orchard 0327 Care Pharmacy | 152777.79 |
| REF-000373 | Lumen 0373 Family Pharmacy | 152777.79 |
| REF-000011 | Timber 0011 Care Pharmacy | 152777.77 |
| REF-000057 | Quartz 0057 Family Pharmacy | 152777.77 |
| REF-000103 | Orchard 0103 Health Pharmacy | 152777.77 |

**Genie SQL**

```sql
WITH pharmacy_exposure AS (
  SELECT
    `pharmacy_id`,
    `pharmacy_name`,
    ROUND(SUM(`estimated_overpayment`), 2) AS `total_estimated_exposure`
  FROM `vandelay`.`rebate_fraud`.`governed_case_features`
  WHERE `pharmacy_id` IS NOT NULL
    AND `pharmacy_name` IS NOT NULL
  GROUP BY `pharmacy_id`, `pharmacy_name`
), ranked_pharmacies AS (
  SELECT
    `pharmacy_id`,
    `pharmacy_name`,
    `total_estimated_exposure`,
    RANK() OVER (ORDER BY `total_estimated_exposure` DESC, `pharmacy_id` ASC) AS `exposure_rank`
  FROM pharmacy_exposure
)
SELECT
  `pharmacy_id`,
  `pharmacy_name`,
  `total_estimated_exposure`
FROM ranked_pharmacies
WHERE `exposure_rank` <= 10
ORDER BY `total_estimated_exposure` DESC, `pharmacy_id` ASC;
```

**Genie result**

| pharmacy_id | pharmacy_name | total_estimated_exposure |
| --- | --- | --- |
| REF-000488 | Pioneer 0488 Health Pharmacy | 207799.14 |
| REF-000396 | Willow 0396 Care Pharmacy | 207668.42 |
| REF-000080 | Elm 0080 Care Pharmacy | 207628.20 |
| REF-000235 | Timber 0235 Health Pharmacy | 202777.79 |
| REF-000281 | Quartz 0281 Community Pharmacy | 152777.79 |
| REF-000327 | Orchard 0327 Care Pharmacy | 152777.79 |
| REF-000373 | Lumen 0373 Family Pharmacy | 152777.79 |
| REF-000011 | Timber 0011 Care Pharmacy | 152777.77 |
| REF-000057 | Quartz 0057 Family Pharmacy | 152777.77 |
| REF-000103 | Orchard 0103 Health Pharmacy | 152777.77 |

**Genie answer:** The **10 pharmacies** with the highest estimated overpayment exposure are shown below, ranked by exposure in descending order.  - **Pioneer 0488 Health Pharmacy** — **$207,799.14** - **Willow 0396 Care Pharmacy** — **$207,668.42** - **Elm 0080 Care Pharmacy** — **$207,628.20** - **Timber 0235 Health Pharmacy** — **$202,777.79** - **Quartz 0281 Community Pharmacy** — **$152,777.79**  Across all 10 shown, exposure ranges from **$152,777.77** to **$207,799.14**, with several pharmacies clustered at about **$152,777.77–$152,777.79**.

**Value match:** Yes

### Q04 — MATCH

**Question:** How have claimed units, supported units, and excess units changed by month?

**Ground-truth result**

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
SELECT
  `review_period`,
  ROUND(SUM(`claimed_units`), 2) AS `claimed_units`,
  ROUND(SUM(`supported_units`), 2) AS `supported_units`,
  ROUND(SUM(`excess_units`), 2) AS `excess_units`
FROM `vandelay`.`rebate_fraud`.`governed_case_features`
WHERE `review_period` IS NOT NULL
GROUP BY `review_period`
ORDER BY `review_period`
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

**Genie answer:** Across the **11 review periods shown** from **2025-11 to 2026-10**, **excess units stayed flat at 2,532.00 units every month**, while **claimed units** were fairly stable in a narrow range from **32,443.00 units** in **2026-01** to **33,044.00 units** in **2026-08**, and **supported units** ranged from **563,403.00 units** in **2026-02** to **570,423.00 units** in **2026-10**. Overall, the monthly pattern is mostly steady with modest month-to-month movement in claimed and supported units, while excess units did not change at all.

**Value match:** Yes

### Q05 — MATCH

**Question:** Compare estimated exposure across regions and show each region's share of total exposure.

**Ground-truth result**

| region | estimated_exposure | exposure_share_percent |
| --- | --- | --- |
| WEST | 3985320.57 | 40.57 |
| SOUTH | 2645632.92 | 26.93 |
| NORTHEAST | 2088988.00 | 21.27 |
| MIDWEST | 1103254.36 | 11.23 |

**Genie SQL**

```sql
SELECT governed_case_features.region, ROUND(SUM(governed_case_features.estimated_overpayment), 2) AS total_estimated_exposure, ROUND(try_divide(100.0 * SUM(governed_case_features.estimated_overpayment),NULLIF(SUM(SUM(governed_case_features.estimated_overpayment)) OVER (), 0)), 2) AS share_of_total_exposure_pct FROM vandelay.rebate_fraud.governed_case_features AS governed_case_features WHERE governed_case_features.region IS NOT NULL GROUP BY governed_case_features.region ORDER BY total_estimated_exposure DESC, governed_case_features.region
```

**Genie result**

| region | total_estimated_exposure | share_of_total_exposure_pct |
| --- | --- | --- |
| WEST | 3985320.57 | 40.57 |
| SOUTH | 2645632.92 | 26.93 |
| NORTHEAST | 2088988.00 | 21.27 |
| MIDWEST | 1103254.36 | 11.23 |

**Genie answer:** Estimated exposure is highest in the **WEST** at **$3,985,320.57** (**40.57%** of total), followed by **SOUTH** at **$2,645,632.92** (**26.93%**), **NORTHEAST** at **$2,088,988.00** (**21.27%**), and **MIDWEST** at **$1,103,254.36** (**11.23%**). Across the 4 regions shown, the **WEST** accounts for the largest share of total exposure, while the **MIDWEST** accounts for the smallest.

**Value match:** Yes

### Q06 — MATCH

**Question:** How much exposure involves cross-channel activity versus single-channel activity?

**Ground-truth result**

| activity_type | total_estimated_exposure |
| --- | --- |
| Cross-channel activity | 5555235.05 |
| Single-channel activity | 4267960.79 |

**Genie SQL**

```sql
SELECT CASE WHEN `has_cross_channel_activity` = true THEN 'cross-channel activity' ELSE 'single-channel activity' END AS `activity_type`, ROUND(SUM(`estimated_overpayment`), 2) AS `total_estimated_exposure` FROM `vandelay`.`rebate_fraud`.`governed_case_features` WHERE `has_cross_channel_activity` IS NOT NULL GROUP BY `has_cross_channel_activity` ORDER BY `total_estimated_exposure` DESC, `activity_type`
```

**Genie result**

| activity_type | total_estimated_exposure |
| --- | --- |
| cross-channel activity | 5555235.05 |
| single-channel activity | 4267960.79 |

**Genie answer:** Exposure is higher for **cross-channel activity** at **$5,555,235.05**, compared with **single-channel activity** at **$4,267,960.79**. Across the **2 activity types** shown, cross-channel activity represents the larger share of estimated exposure.

**Value match:** Yes

### Q07 — MATCH

**Question:** Show the ten case records with the highest estimated overpayment exposure, breaking ties by excess units.

**Ground-truth result**

| case_id | pharmacy_name | product_code | review_period | excess_units | estimated_overpayment |
| --- | --- | --- | --- | --- | --- |
| 50375d16e6cdb9bee5d626b3003d73be91afc3c7442f95f4bc596f718835300d | Timber 0235 Health Pharmacy | 99999-0301-01 | 2025-11 | 495.00 | 152777.79 |
| 50dce036c9dbdb79a9a7cf99c7058309c5dc91996dbad1722e58a5d837021142 | Orchard 0327 Care Pharmacy | 99999-0301-01 | 2026-01 | 495.00 | 152777.79 |
| 9b47147353c3e4fd0e1cf3908b99d2b8b593c280d7d7132388a47e81377f0ecd | Quartz 0281 Community Pharmacy | 99999-0102-01 | 2025-12 | 495.00 | 152777.79 |
| cd6705dddbaa2aead8d8aae93791d84adc26d9fc2a5ca8f5483d3c256402407a | Lumen 0373 Family Pharmacy | 99999-0102-01 | 2026-02 | 495.00 | 152777.79 |
| 0b17368ac8b483e680b26da562e0ed2a1b14c82c13beb5edb23ec0e36df61877 | Orchard 0103 Health Pharmacy | 99999-0301-01 | 2026-07 | 495.00 | 152777.77 |
| 31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64 | Aster 0241 Family Pharmacy | 99999-0102-01 | 2026-10 | 495.00 | 152777.77 |
| 3b7ba9fd5175ee3bb5cd1e61e632775417cb128c762a234201f66d7f4a8ea9f3 | Harbor 0419 Health Pharmacy | 99999-0301-01 | 2026-03 | 495.00 | 152777.77 |
| 46db4cb8b07bb599325af9b59c954e800e9f7261fbc6aca6bb1bc003e71376ed | Timber 0011 Care Pharmacy | 99999-0301-01 | 2026-05 | 495.00 | 152777.77 |
| 56801fee4f5645973398022792b2e071f4f96380e0177a682a1816fcfc97faa1 | Lumen 0149 Community Pharmacy | 99999-0102-01 | 2026-08 | 495.00 | 152777.77 |
| 77039103eb6625099e758d12b1e248d2a8b6f5d5deffc2534191156fcc88d014 | Quartz 0057 Family Pharmacy | 99999-0102-01 | 2026-06 | 495.00 | 152777.77 |

**Genie SQL**

```sql
SELECT `case_id`, `pharmacy_id`, `pharmacy_name`, `entity_status`, `region`, `state_code`, `product_code`, `review_period`, `claim_count`, `medical_claim_count`, `pharmacy_claim_count`, `channel_count`, `source_identity_count`, `claimed_units`, `supported_units`, `excess_units`, `claimed_rebate_amount`, ROUND(`estimated_overpayment`, 2) AS `estimated_overpayment`, `has_cross_channel_activity`, `matched_cross_channel_pairs`, `has_multiple_source_identities`, `manufacturer_units`, `wholesaler_units`
FROM `vandelay`.`rebate_fraud`.`governed_case_features`
WHERE `estimated_overpayment` IS NOT NULL
  AND `excess_units` IS NOT NULL
ORDER BY `estimated_overpayment` DESC, `excess_units` DESC, `case_id` ASC
LIMIT 10
```

**Genie result**

| case_id | pharmacy_id | pharmacy_name | entity_status | region | state_code | product_code | review_period | claim_count | medical_claim_count | pharmacy_claim_count | channel_count | source_identity_count | claimed_units | supported_units | excess_units | claimed_rebate_amount | estimated_overpayment | has_cross_channel_activity | matched_cross_channel_pairs | has_multiple_source_identities | manufacturer_units | wholesaler_units |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 50375d16e6cdb9bee5d626b3003d73be91afc3c7442f95f4bc596f718835300d | REF-000235 | Timber 0235 Health Pharmacy | ACTIVE | WEST | OR | 99999-0301-01 | 2025-11 | 2 | 1 | 1 | 2 | 1 | 540.00 | 45.00 | 495.00 | 166666.68 | 152777.79 | true | 1 | false | 45.00 | 0.00 |
| 50dce036c9dbdb79a9a7cf99c7058309c5dc91996dbad1722e58a5d837021142 | REF-000327 | Orchard 0327 Care Pharmacy | ACTIVE | NORTHEAST | MA | 99999-0301-01 | 2026-01 | 2 | 1 | 1 | 2 | 1 | 540.00 | 45.00 | 495.00 | 166666.68 | 152777.79 | true | 1 | false | 45.00 | 0.00 |
| 9b47147353c3e4fd0e1cf3908b99d2b8b593c280d7d7132388a47e81377f0ecd | REF-000281 | Quartz 0281 Community Pharmacy | ACTIVE | NORTHEAST | NY | 99999-0102-01 | 2025-12 | 2 | 1 | 1 | 2 | 1 | 540.00 | 45.00 | 495.00 | 166666.68 | 152777.79 | true | 1 | false | 45.00 | 0.00 |
| cd6705dddbaa2aead8d8aae93791d84adc26d9fc2a5ca8f5483d3c256402407a | REF-000373 | Lumen 0373 Family Pharmacy | ACTIVE | SOUTH | GA | 99999-0102-01 | 2026-02 | 2 | 1 | 1 | 2 | 1 | 540.00 | 45.00 | 495.00 | 166666.68 | 152777.79 | true | 1 | false | 45.00 | 0.00 |
| 0b17368ac8b483e680b26da562e0ed2a1b14c82c13beb5edb23ec0e36df61877 | REF-000103 | Orchard 0103 Health Pharmacy | ACTIVE | NORTHEAST | MA | 99999-0301-01 | 2026-07 | 2 | 1 | 1 | 2 | 1 | 540.00 | 45.00 | 495.00 | 166666.66 | 152777.77 | true | 1 | false | 45.00 | 0.00 |
| 31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64 | REF-000241 | Aster 0241 Family Pharmacy | ACTIVE | WEST | AZ | 99999-0102-01 | 2026-10 | 2 | 1 | 1 | 2 | 1 | 540.00 | 45.00 | 495.00 | 166666.66 | 152777.77 | true | 1 | false | 45.00 | 0.00 |
| 3b7ba9fd5175ee3bb5cd1e61e632775417cb128c762a234201f66d7f4a8ea9f3 | REF-000419 | Harbor 0419 Health Pharmacy | ACTIVE | WEST | CO | 99999-0301-01 | 2026-03 | 2 | 1 | 1 | 2 | 1 | 540.00 | 45.00 | 495.00 | 166666.66 | 152777.77 | true | 1 | false | 45.00 | 0.00 |
| 46db4cb8b07bb599325af9b59c954e800e9f7261fbc6aca6bb1bc003e71376ed | REF-000011 | Timber 0011 Care Pharmacy | CLOSED | WEST | OR | 99999-0301-01 | 2026-05 | 2 | 1 | 1 | 2 | 1 | 540.00 | 45.00 | 495.00 | 166666.66 | 152777.77 | true | 1 | false | 45.00 | 0.00 |
| 56801fee4f5645973398022792b2e071f4f96380e0177a682a1816fcfc97faa1 | REF-000149 | Lumen 0149 Community Pharmacy | ACTIVE | SOUTH | GA | 99999-0102-01 | 2026-08 | 2 | 1 | 1 | 2 | 1 | 540.00 | 45.00 | 495.00 | 166666.66 | 152777.77 | true | 1 | false | 45.00 | 0.00 |
| 77039103eb6625099e758d12b1e248d2a8b6f5d5deffc2534191156fcc88d014 | REF-000057 | Quartz 0057 Family Pharmacy | ACTIVE | NORTHEAST | NY | 99999-0102-01 | 2026-06 | 2 | 1 | 1 | 2 | 1 | 540.00 | 45.00 | 495.00 | 166666.66 | 152777.77 | true | 1 | false | 45.00 | 0.00 |

**Genie answer:** These are the **10 case records** with the highest estimated overpayment exposure in the available results, ranked by estimated overpayment and then excess units. Examples include: - **Timber 0235 Health Pharmacy** (OR, **2025-11**) — **$152,777.79** estimated overpayment, **495.00 units** excess - **Orchard 0327 Care Pharmacy** (MA, **2026-01**) — **$152,777.79** estimated overpayment, **495.00 units** excess - **Quartz 0281 Community Pharmacy** (NY, **2025-12**) — **$152,777.79** estimated overpayment, **495.00 units** excess - **Lumen 0373 Family Pharmacy** (GA, **2026-02**) — **$152,777.79** estimated overpayment, **495.00 units** excess - **Orchard 0103 Health Pharmacy** (MA, **2026-07**) — **$152,777.77** estimated overpayment, **495.00 units** excess Across all 10 records, estimated overpayment is tightly clustered between **$152,777.77** and **$152,777.79**, and every case shows **495.00 units** of excess volume with cross-channel activity present.

**Value match:** Yes

### Q08 — MATCH

**Question:** For case 31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64, show its quantities, channel evidence, identity evidence, entity status, and estimated exposure.

**Ground-truth result**

| case_id | pharmacy_name | entity_status | product_code | review_period | claimed_units | supported_units | excess_units | manufacturer_units | wholesaler_units | has_cross_channel_activity | matched_cross_channel_pairs | has_multiple_source_identities | source_identity_count | estimated_overpayment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64 | Aster 0241 Family Pharmacy | ACTIVE | 99999-0102-01 | 2026-10 | 540.00 | 45.00 | 495.00 | 45.00 | 0.00 | true | 1 | false | 1 | 152777.77 |

**Genie SQL**

```sql
SELECT governed_case_features.case_id, governed_case_features.pharmacy_id, governed_case_features.pharmacy_name, governed_case_features.product_code, governed_case_features.review_period, governed_case_features.claimed_units, governed_case_features.manufacturer_units, governed_case_features.wholesaler_units, governed_case_features.supported_units, governed_case_features.excess_units, governed_case_features.claim_count, governed_case_features.medical_claim_count, governed_case_features.pharmacy_claim_count, governed_case_features.channel_count, governed_case_features.has_cross_channel_activity, governed_case_features.matched_cross_channel_pairs, governed_case_features.source_identity_count, governed_case_features.has_multiple_source_identities, governed_case_features.entity_status, ROUND(governed_case_features.estimated_overpayment, 2) AS estimated_overpayment FROM vandelay.rebate_fraud.governed_case_features AS governed_case_features WHERE governed_case_features.case_id = '31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64'
```

**Genie result**

| case_id | pharmacy_id | pharmacy_name | product_code | review_period | claimed_units | manufacturer_units | wholesaler_units | supported_units | excess_units | claim_count | medical_claim_count | pharmacy_claim_count | channel_count | has_cross_channel_activity | matched_cross_channel_pairs | source_identity_count | has_multiple_source_identities | entity_status | estimated_overpayment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64 | REF-000241 | Aster 0241 Family Pharmacy | 99999-0102-01 | 2026-10 | 540.00 | 45.00 | 0.00 | 45.00 | 495.00 | 2 | 1 | 1 | 2 | true | 1 | 1 | false | ACTIVE | 152777.77 |

**Genie answer:** For case **31881b473deba7f758f4ac3cb385346641f12c35a88f7f70e9a5245f2602ba64** in review period **2026-10**, claimed units are **540.00 units**, manufacturer units are **45.00 units**, wholesaler units are **0.00 units**, supported units are **45.00 units**, excess units are **495.00 units**, and estimated exposure is **$152,777.77**. Channel evidence shows **2** channels, **has_cross_channel_activity = true**, and **1** matched cross-channel pair; identity evidence shows **source_identity_count = 1** and **has_multiple_source_identities = false**, and entity status is **ACTIVE**.

**Value match:** Yes

### Q09 — MATCH

**Question:** How many cases involve multiple source identities, and how does their average estimated exposure compare with other cases?

**Ground-truth result**

| case_group | case_count | avg_estimated_exposure |
| --- | --- | --- |
| Other cases | 19686 | 493.91 |
| Multiple source identities | 2159 | 46.32 |

**Genie SQL**

```sql
SELECT CASE WHEN governed_case_features.has_multiple_source_identities = true THEN 'Multiple source identities' ELSE 'Other cases' END AS case_group, COUNT(DISTINCT governed_case_features.case_id) AS case_count, ROUND(AVG(governed_case_features.estimated_overpayment), 2) AS avg_estimated_exposure FROM vandelay.rebate_fraud.governed_case_features AS governed_case_features GROUP BY CASE WHEN governed_case_features.has_multiple_source_identities = true THEN 'Multiple source identities' ELSE 'Other cases' END ORDER BY CASE WHEN CASE WHEN governed_case_features.has_multiple_source_identities = true THEN 'Multiple source identities' ELSE 'Other cases' END = 'Multiple source identities' THEN 0 ELSE 1 END, case_group
```

**Genie result**

| case_group | case_count | avg_estimated_exposure |
| --- | --- | --- |
| Multiple source identities | 2159 | 46.32 |
| Other cases | 19686 | 493.91 |

**Genie answer:** **2,159** cases involve **multiple source identities**, with an average estimated exposure of **$46.32**. **Other cases** account for **19,686** cases and have a much higher average estimated exposure of **$493.91**, so cases with multiple source identities show lower average exposure in this result.

**Value match:** Yes

### Q10 — MATCH

**Question:** Compare suspected cases for active, pending, and closed pharmacy entities.

**Ground-truth result**

| entity_status | suspected_case_count |
| --- | --- |
| ACTIVE | 20973 |
| CLOSED | 872 |

**Genie SQL**

```sql
SELECT
  `entity_status`,
  COUNT(DISTINCT `case_id`) AS `suspected_case_count`
FROM `vandelay`.`rebate_fraud`.`governed_case_features`
WHERE `entity_status` IS NOT NULL
  AND (
    `entity_status` ILIKE '%ACTIVE%'
    OR `entity_status` ILIKE '%PENDING%'
    OR `entity_status` ILIKE '%CLOSED%'
  )
GROUP BY `entity_status`
ORDER BY `suspected_case_count` DESC, `entity_status`
```

**Genie result**

| entity_status | suspected_case_count |
| --- | --- |
| ACTIVE | 20973 |
| CLOSED | 872 |

**Genie answer:** Based on the visible results, **ACTIVE** pharmacy entities have **20,973** suspected cases, while **CLOSED** entities have **872**. No **PENDING** pharmacy entities appear in the returned data. Among the statuses shown, suspected cases are heavily concentrated in **ACTIVE** entities.

**Value match:** Yes

### Q11 — MATCH

**Question:** By month, how many pharmacy and product combinations have claimed units greater than supported units?

**Ground-truth result**

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
SELECT `review_period`, COUNT(DISTINCT CONCAT(`pharmacy_id`, '||', `product_code`)) AS `pharmacy_product_combination_count`
FROM `vandelay`.`rebate_fraud`.`governed_case_features`
WHERE `review_period` IS NOT NULL
  AND `pharmacy_id` IS NOT NULL
  AND `product_code` IS NOT NULL
  AND `claimed_units` > `supported_units`
GROUP BY `review_period`
ORDER BY `review_period`
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

**Genie answer:** Across the **11 review periods shown** (from **2025-11** to **2026-10**), the count is **13 pharmacy-product combinations** in every month where claimed units are greater than supported units. This is a complete sample of the returned data, and there is **no month-to-month variation** in the count across the review periods present.  - **2025-11:** **13** - **2025-12:** **13** - **2026-01:** **13** - **2026-02:** **13** - **2026-03:** **13**

**Value match:** Yes

### Q12 — MATCH

**Question:** Which cases combine excess claimed units, cross-channel activity, and multiple source identities?

**Ground-truth result**

| case_id | pharmacy_name | product_code | review_period | excess_units | estimated_overpayment |
| --- | --- | --- | --- | --- | --- |
| 5ca92443ba6a6b87bd3dfd72715aa4c530ba2cdc4dae4235ae3c9b375ad1c12a | Willow 0172 Health Pharmacy | 99999-0301-01 | 2026-06 | 20.00 | 50000.00 |
| 617c03c477d1fa9d29e87f75ee334eaa52792f086725f8870ad6bb3ee18a92f0 | Timber 0235 Health Pharmacy | 99999-0101-01 | 2025-12 | 21.00 | 50000.00 |

**Genie SQL**

```sql
SELECT `case_id`, `pharmacy_id`, `pharmacy_name`, `product_code`, `review_period`, `claimed_units`, `supported_units`, `excess_units`, `matched_cross_channel_pairs`, `source_identity_count`, `claimed_rebate_amount`, ROUND(`estimated_overpayment`, 2) AS `estimated_overpayment` FROM `vandelay`.`rebate_fraud`.`governed_case_features` WHERE `claimed_units` > `supported_units` AND `has_cross_channel_activity` = TRUE AND `has_multiple_source_identities` = TRUE ORDER BY `estimated_overpayment` DESC, `case_id`
```

**Genie result**

| case_id | pharmacy_id | pharmacy_name | product_code | review_period | claimed_units | supported_units | excess_units | matched_cross_channel_pairs | source_identity_count | claimed_rebate_amount | estimated_overpayment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5ca92443ba6a6b87bd3dfd72715aa4c530ba2cdc4dae4235ae3c9b375ad1c12a | REF-000172 | Willow 0172 Health Pharmacy | 99999-0301-01 | 2026-06 | 40.00 | 20.00 | 20.00 | 1 | 2 | 100000.00 | 50000.00 |
| 617c03c477d1fa9d29e87f75ee334eaa52792f086725f8870ad6bb3ee18a92f0 | REF-000235 | Timber 0235 Health Pharmacy | 99999-0101-01 | 2025-12 | 42.00 | 21.00 | 21.00 | 1 | 2 | 100000.00 | 50000.00 |

**Genie answer:** There are **2 cases** that meet all three conditions: excess claimed units, cross-channel activity, and multiple source identities. - **Willow 0172 Health Pharmacy** (case **5ca92443...**), product **99999-0301-01**, review period **2026-06**: **20.00 units** in excess, **1** cross-channel match, **2** source identities, and **$50,000.00** estimated overpayment. - **Timber 0235 Health Pharmacy** (case **617c03c4...**), product **99999-0101-01**, review period **2025-12**: **21.00 units** in excess, **1** cross-channel match, **2** source identities, and **$50,000.00** estimated overpayment. Both cases show the same estimated overpayment and the same counts for cross-channel matches and source identities.

**Value match:** Yes

### Q13 — MATCH

**Question:** How many case records are missing pharmacy ID, pharmacy name, region, or state code?

**Ground-truth result**

| missing_case_record_count |
| --- |
| 0 |

**Genie SQL**

```sql
SELECT COUNT(*) AS `missing_case_record_count`
FROM `vandelay`.`rebate_fraud`.`governed_case_features`
WHERE `pharmacy_id` IS NULL
   OR `pharmacy_name` IS NULL
   OR `region` IS NULL
   OR `state_code` IS NULL
```

**Genie result**

| missing_case_record_count |
| --- |
| 0 |

**Genie answer:** There are **0** case records missing **pharmacy ID**, **pharmacy name**, **region**, or **state code**. In the result shown, missing location or pharmacy identification details do **not** appear to be a data gap for case records.

**Value match:** Yes

### Q14 — MATCH

**Question:** How many case records are missing claimed units, supported units, excess units, or estimated exposure?

**Ground-truth result**

| missing_claimed_units | missing_supported_units | missing_excess_units | missing_estimated_exposure |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 0 |

**Genie SQL**

```sql
SELECT
  COUNT_IF(`claimed_units` IS NULL) AS `missing_claimed_units`,
  COUNT_IF(`supported_units` IS NULL) AS `missing_supported_units`,
  COUNT_IF(`excess_units` IS NULL) AS `missing_excess_units`,
  COUNT_IF(`estimated_overpayment` IS NULL) AS `missing_estimated_exposure`
FROM `vandelay`.`rebate_fraud`.`governed_case_features`
```

**Genie result**

| missing_claimed_units | missing_supported_units | missing_excess_units | missing_estimated_exposure |
| --- | --- | --- | --- |
| 0 | 0 | 0 | 0 |

**Genie answer:** There are **0** case records missing claimed units, **0** case records missing supported units, **0** case records missing excess units, and **0** case records missing estimated exposure. Based on this result, the reviewed case data shows **no missing values** across all four fields.

**Value match:** Yes

### Q15 — MATCH

**Question:** For each product, compare total claimed units, manufacturer units, wholesaler units, supported units, and excess units.

**Ground-truth result**

| product_code | claimed_units | manufacturer_units | wholesaler_units | supported_units | excess_units |
| --- | --- | --- | --- | --- | --- |
| 99999-0101-01 | 90413.00 | 649951.00 | 904399.00 | 1554350.00 | 7101.00 |
| 99999-0102-01 | 90003.00 | 650604.00 | 903638.00 | 1554242.00 | 7408.00 |
| 99999-0201-01 | 90093.00 | 658156.00 | 901944.00 | 1560100.00 | 6620.00 |
| 99999-0301-01 | 90324.00 | 656381.00 | 912264.00 | 1568645.00 | 6723.00 |

**Genie SQL**

```sql
SELECT
  `product_code`,
  SUM(`claimed_units`) AS `total_claimed_units`,
  SUM(`manufacturer_units`) AS `total_manufacturer_units`,
  SUM(`wholesaler_units`) AS `total_wholesaler_units`,
  SUM(`supported_units`) AS `total_supported_units`,
  SUM(`excess_units`) AS `total_excess_units`
FROM `vandelay`.`rebate_fraud`.`governed_case_features`
WHERE `product_code` IS NOT NULL
GROUP BY `product_code`
ORDER BY `product_code`
```

**Genie result**

| product_code | total_claimed_units | total_manufacturer_units | total_wholesaler_units | total_supported_units | total_excess_units |
| --- | --- | --- | --- | --- | --- |
| 99999-0101-01 | 90413.00 | 649951.00 | 904399.00 | 1554350.00 | 7101.00 |
| 99999-0102-01 | 90003.00 | 650604.00 | 903638.00 | 1554242.00 | 7408.00 |
| 99999-0201-01 | 90093.00 | 658156.00 | 901944.00 | 1560100.00 | 6620.00 |
| 99999-0301-01 | 90324.00 | 656381.00 | 912264.00 | 1568645.00 | 6723.00 |

**Genie answer:** Across the **4 products** shown, supported units are much higher than claimed units for every product, and excess units range from **6,620.00 units** to **7,408.00 units**.  - **99999-0101-01**: claimed **90,413.00 units**, manufacturer **649,951.00 units**, wholesaler **904,399.00 units**, supported **1,554,350.00 units**, excess **7,101.00 units** - **99999-0102-01**: claimed **90,003.00 units**, manufacturer **650,604.00 units**, wholesaler **903,638.00 units**, supported **1,554,242.00 units**, excess **7,408.00 units** - **99999-0201-01**: claimed **90,093.00 units**, manufacturer **658,156.00 units**, wholesaler **901,944.00 units**, supported **1,560,100.00 units**, excess **6,620.00 units** - **99999-0301-01**: claimed **90,324.00 units**, manufacturer **656,381.00 units**, wholesaler **912,264.00 units**, supported **1,568,645.00 units**, excess **6,723.00 units**

**Value match:** Yes

