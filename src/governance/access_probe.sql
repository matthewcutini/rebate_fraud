-- Used to prove permission hiding separately from object existence.
SELECT count(*) AS harmless_probe_rows
FROM vandelay.rebate_fraud.governance_permission_probe;
