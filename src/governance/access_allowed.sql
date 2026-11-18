-- Runs as the dedicated non-admin service principal.
DELETE FROM vandelay.rebate_fraud.governance_access_test_results
WHERE test_principal = current_user();

INSERT INTO vandelay.rebate_fraud.governance_access_test_results
WITH visible AS (
  SELECT *
  FROM vandelay.rebate_fraud.governed_case_features
), masked_join AS (
  SELECT count(*) AS joined_rows
  FROM visible left_side
  INNER JOIN visible right_side
    ON left_side.pharmacy_phone = right_side.pharmacy_phone
   AND left_side.case_id < right_side.case_id
)
SELECT
  current_user() AS test_principal,
  count(*) AS visible_rows,
  count(DISTINCT region) AS visible_regions,
  min(pharmacy_phone) AS phone_example,
  min(pharmacy_address) AS address_example,
  (SELECT joined_rows FROM masked_join) AS masked_column_join_rows,
  current_timestamp() AS tested_at
FROM visible;

SELECT count(*) AS evidence_rows_written
FROM vandelay.rebate_fraud.governance_access_test_results
WHERE test_principal = current_user();
