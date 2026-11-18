-- Raw source exports are preserved as strings with file lineage and ingestion time.

CREATE OR REFRESH STREAMING TABLE bronze_medical_claims (
  CONSTRAINT compatible_medical_schema EXPECT (_rescued_data IS NULL) ON VIOLATION FAIL UPDATE
)
COMMENT 'Medical-channel rebate claims exactly as landed.'
AS
SELECT
  *,
  _metadata.file_path AS _source_file,
  current_timestamp() AS _ingested_at
FROM STREAM read_files(
  '${landing_path}/*/medical_claims/*.jsonl',
  format => 'json',
  schemaHints => 'medClaimId STRING, billingEntityName STRING, billingNpi STRING, serviceFromDate STRING, productCode STRING, unitsBilled STRING, rebateUnitsRequested STRING, rebateAmount STRING, entityAddress STRING, entityPhone STRING, entityFax STRING, receivedTimestamp STRING, _rescued_data STRING'
);

CREATE OR REFRESH STREAMING TABLE bronze_pharmacy_claims (
  CONSTRAINT compatible_pharmacy_schema EXPECT (_rescued_data IS NULL) ON VIOLATION FAIL UPDATE
)
COMMENT 'Pharmacy-channel rebate claims exactly as landed.'
AS
SELECT
  *,
  _metadata.file_path AS _source_file,
  current_timestamp() AS _ingested_at
FROM STREAM read_files(
  '${landing_path}/*/pharmacy_claims/*.csv',
  format => 'csv',
  header => true,
  schemaHints => 'RX_CLAIM_NBR STRING, PHARMACY_NAME STRING, NCPDP_ID STRING, FILL_DATE STRING, PRODUCT_NDC STRING, QTY_DISPENSED STRING, REBATE_UNITS STRING, REBATE_AMT STRING, STORE_ADDR STRING, PHONE_NBR STRING, FAX_NBR STRING, SUBMISSION_TS STRING, _rescued_data STRING'
);

CREATE OR REFRESH STREAMING TABLE bronze_manufacturer_sales (
  CONSTRAINT compatible_sales_schema EXPECT (_rescued_data IS NULL) ON VIOLATION FAIL UPDATE
)
COMMENT 'Manufacturer sales and returns exactly as landed.'
AS
SELECT
  *,
  _metadata.file_path AS _source_file,
  current_timestamp() AS _ingested_at
FROM STREAM read_files(
  '${landing_path}/*/manufacturer_sales/*.csv',
  format => 'csv',
  header => true,
  schemaHints => 'SALES_DOC_NBR STRING, SOLD_TO_ACCT STRING, SHIP_TO_NAME STRING, SHIP_TO_ADDR STRING, MATERIAL_CD STRING, QTY_SHIPPED STRING, NET_AMT STRING, SHIP_DT STRING, DOC_TYPE STRING, _rescued_data STRING'
);

CREATE OR REFRESH STREAMING TABLE bronze_wholesaler_shipments (
  CONSTRAINT compatible_wholesaler_schema EXPECT (_rescued_data IS NULL) ON VIOLATION FAIL UPDATE
)
COMMENT 'Wholesaler 867 distribution records exactly as landed.'
AS
SELECT
  *,
  _metadata.file_path AS _source_file,
  current_timestamp() AS _ingested_at
FROM STREAM read_files(
  '${landing_path}/*/wholesaler_distribution/*.psv',
  format => 'csv',
  header => true,
  sep => '|',
  schemaHints => 'Transaction_ID STRING, Wholesaler_Customer_ID STRING, Customer_Name STRING, Customer_Address STRING, Customer_Phone STRING, Customer_Fax STRING, NDC STRING, Transaction_Type STRING, Quantity STRING, Invoice_Date STRING, _rescued_data STRING'
);

CREATE OR REFRESH STREAMING TABLE bronze_pharmacy_reference (
  CONSTRAINT compatible_reference_schema EXPECT (_rescued_data IS NULL) ON VIOLATION FAIL UPDATE
)
COMMENT 'Monthly pharmacy identity reference snapshots exactly as landed.'
AS
SELECT
  *,
  _metadata.file_path AS _source_file,
  current_timestamp() AS _ingested_at
FROM STREAM read_files(
  '${landing_path}/*/pharmacy_reference/*.jsonl',
  format => 'json',
  schemaHints => 'sourceEntityId STRING, legalName STRING, doingBusinessAs STRING, address STRING, phone STRING, fax STRING, status STRING, effectiveDate STRING, closedDate STRING, _rescued_data STRING'
);

CREATE OR REFRESH STREAMING TABLE bronze_control_manifest (
  CONSTRAINT compatible_manifest_schema EXPECT (_rescued_data IS NULL) ON VIOLATION FAIL UPDATE
)
COMMENT 'Source control manifests written after each complete delivery period.'
AS
SELECT
  *,
  _metadata.file_path AS _source_file,
  current_timestamp() AS _ingested_at
FROM STREAM read_files(
  '${landing_path}/*/manifest/*.json',
  format => 'json',
  multiLine => true,
  schemaHints => 'period STRING, deliveryState STRING, completedTimestamp STRING, files ARRAY<STRUCT<fileName:STRING,relativePath:STRING,recordCount:BIGINT,quantityTotal:BIGINT,amountTotal:STRING,bytes:BIGINT,sha256:STRING>>, controlTotals STRUCT<fileCount:BIGINT,recordCount:BIGINT,claimRecordCount:BIGINT,claimAmountTotal:STRING>, _rescued_data STRING'
);
