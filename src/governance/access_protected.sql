-- Expected to fail because the principal has no SELECT on silver tables.
SELECT count(*) AS protected_table_rows
FROM vandelay.rebate_fraud.silver_claims;
