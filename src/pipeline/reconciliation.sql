-- Control totals prove complete delivery and make any mismatch pipeline-visible.

CREATE OR REFRESH MATERIALIZED VIEW reconciliation_claims (
  CONSTRAINT claims_reconciled EXPECT (reconciliation_status = 'RECONCILED') ON VIOLATION FAIL UPDATE
)
COMMENT 'Per-period claim control totals reconciled to bronze, silver and quarantine.'
AS
WITH manifest AS (
  SELECT
    period,
    controlTotals.claimRecordCount AS expected_claim_rows,
    try_cast(controlTotals.claimAmountTotal AS DECIMAL(20, 2)) AS expected_claim_amount
  FROM bronze_control_manifest
), landed AS (
  SELECT
    regexp_extract(_source_file, '/(\\d{4}-\\d{2})/', 1) AS period,
    count(*) AS landed_claim_rows,
    sum(try_cast(rebateAmount AS DECIMAL(20, 2))) AS landed_claim_amount
  FROM bronze_medical_claims
  GROUP BY 1
  UNION ALL
  SELECT
    regexp_extract(_source_file, '/(\\d{4}-\\d{2})/', 1),
    count(*),
    sum(try_cast(REBATE_AMT AS DECIMAL(20, 2)))
  FROM bronze_pharmacy_claims
  GROUP BY 1
), landed_by_period AS (
  SELECT period, sum(landed_claim_rows) AS landed_claim_rows, sum(landed_claim_amount) AS landed_claim_amount
  FROM landed
  GROUP BY period
), loaded AS (
  SELECT delivery_period AS period, count(*) AS loaded_claim_rows
  FROM silver_claims
  GROUP BY delivery_period
), quarantined AS (
  SELECT regexp_extract(_source_file, '/(\\d{4}-\\d{2})/', 1) AS period, count(*) AS quarantined_claim_rows
  FROM quarantine_claims
  GROUP BY 1
)
SELECT
  manifest.period,
  manifest.expected_claim_rows,
  coalesce(landed_by_period.landed_claim_rows, 0) AS landed_claim_rows,
  coalesce(loaded.loaded_claim_rows, 0) AS loaded_claim_rows,
  coalesce(quarantined.quarantined_claim_rows, 0) AS quarantined_claim_rows,
  manifest.expected_claim_amount,
  coalesce(landed_by_period.landed_claim_amount, 0) AS landed_claim_amount,
  CASE
    WHEN coalesce(landed_by_period.landed_claim_rows, 0) = manifest.expected_claim_rows
     AND coalesce(loaded.loaded_claim_rows, 0) + coalesce(quarantined.quarantined_claim_rows, 0) = manifest.expected_claim_rows
     AND coalesce(landed_by_period.landed_claim_amount, 0) = manifest.expected_claim_amount
    THEN 'RECONCILED'
    ELSE 'BREAK'
  END AS reconciliation_status
FROM manifest
LEFT JOIN landed_by_period USING (period)
LEFT JOIN loaded USING (period)
LEFT JOIN quarantined USING (period);
