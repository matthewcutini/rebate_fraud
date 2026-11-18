-- Claims from both channels are conformed through append flows. Approved invalid
-- records are dropped by expectations and independently retained in quarantine.

CREATE OR REFRESH STREAMING TABLE silver_claims_conformed (
  claim_id STRING,
  claim_channel STRING,
  source_entity_id STRING,
  pharmacy_name STRING,
  pharmacy_address STRING,
  phone STRING,
  fax STRING,
  service_date DATE,
  product_code STRING,
  dispensed_units DECIMAL(18, 2),
  rebate_units DECIMAL(18, 2),
  rebate_amount DECIMAL(18, 2),
  submitted_at TIMESTAMP,
  delivery_period STRING,
  _source_file STRING,
  _ingested_at TIMESTAMP,
  had_trailing_whitespace BOOLEAN,
  is_late BOOLEAN,
  has_contact_gap BOOLEAN,
  CONSTRAINT claim_id_present EXPECT (claim_id IS NOT NULL AND claim_id <> '') ON VIOLATION DROP ROW,
  CONSTRAINT positive_rebate_units EXPECT (rebate_units > 0) ON VIOLATION DROP ROW,
  CONSTRAINT valid_service_date EXPECT (service_date IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT known_product_code EXPECT (product_code IN ('99999-0101-01', '99999-0102-01', '99999-0201-01', '99999-0301-01')) ON VIOLATION DROP ROW,
  CONSTRAINT timely_claim EXPECT (NOT is_late),
  CONSTRAINT clean_pharmacy_name EXPECT (NOT had_trailing_whitespace),
  CONSTRAINT contact_available EXPECT (NOT has_contact_gap)
)
COMMENT 'Valid, typed and conformed claim rows before exact retransmission deduplication.';

CREATE FLOW medical_claims_flow AS INSERT INTO silver_claims_conformed BY NAME
SELECT
  trim(medClaimId) AS claim_id,
  'MEDICAL' AS claim_channel,
  trim(billingNpi) AS source_entity_id,
  trim(billingEntityName) AS pharmacy_name,
  upper(trim(entityAddress)) AS pharmacy_address,
  regexp_replace(coalesce(entityPhone, ''), '[^0-9]', '') AS phone,
  regexp_replace(coalesce(entityFax, ''), '[^0-9]', '') AS fax,
  try_cast(serviceFromDate AS DATE) AS service_date,
  upper(trim(productCode)) AS product_code,
  try_cast(unitsBilled AS DECIMAL(18, 2)) AS dispensed_units,
  try_cast(rebateUnitsRequested AS DECIMAL(18, 2)) AS rebate_units,
  try_cast(rebateAmount AS DECIMAL(18, 2)) AS rebate_amount,
  try_cast(receivedTimestamp AS TIMESTAMP) AS submitted_at,
  regexp_extract(_source_file, '/(\\d{4}-\\d{2})/', 1) AS delivery_period,
  _source_file,
  _ingested_at,
  billingEntityName <> rtrim(billingEntityName) AS had_trailing_whitespace,
  date_format(try_cast(serviceFromDate AS DATE), 'yyyy-MM') < regexp_extract(_source_file, '/(\\d{4}-\\d{2})/', 1) AS is_late,
  coalesce(trim(entityPhone), '') = '' OR coalesce(trim(entityFax), '') = '' AS has_contact_gap
FROM STREAM(bronze_medical_claims);

CREATE FLOW pharmacy_claims_flow AS INSERT INTO silver_claims_conformed BY NAME
SELECT
  trim(RX_CLAIM_NBR) AS claim_id,
  'PHARMACY' AS claim_channel,
  trim(NCPDP_ID) AS source_entity_id,
  trim(PHARMACY_NAME) AS pharmacy_name,
  upper(trim(STORE_ADDR)) AS pharmacy_address,
  regexp_replace(coalesce(PHONE_NBR, ''), '[^0-9]', '') AS phone,
  regexp_replace(coalesce(FAX_NBR, ''), '[^0-9]', '') AS fax,
  try_cast(FILL_DATE AS DATE) AS service_date,
  upper(trim(PRODUCT_NDC)) AS product_code,
  try_cast(QTY_DISPENSED AS DECIMAL(18, 2)) AS dispensed_units,
  try_cast(REBATE_UNITS AS DECIMAL(18, 2)) AS rebate_units,
  try_cast(REBATE_AMT AS DECIMAL(18, 2)) AS rebate_amount,
  try_cast(SUBMISSION_TS AS TIMESTAMP) AS submitted_at,
  regexp_extract(_source_file, '/(\\d{4}-\\d{2})/', 1) AS delivery_period,
  _source_file,
  _ingested_at,
  PHARMACY_NAME <> rtrim(PHARMACY_NAME) AS had_trailing_whitespace,
  date_format(try_cast(FILL_DATE AS DATE), 'yyyy-MM') < regexp_extract(_source_file, '/(\\d{4}-\\d{2})/', 1) AS is_late,
  coalesce(trim(PHONE_NBR), '') = '' OR coalesce(trim(FAX_NBR), '') = '' AS has_contact_gap
FROM STREAM(bronze_pharmacy_claims);

CREATE OR REFRESH MATERIALIZED VIEW silver_claims
COMMENT 'Conformed claims deduplicated on channel and source claim identifier.'
AS
SELECT * EXCEPT (_dedupe_rank)
FROM (
  SELECT
    *,
    row_number() OVER (
      PARTITION BY claim_channel, claim_id
      ORDER BY submitted_at, _source_file
    ) AS _dedupe_rank
  FROM silver_claims_conformed
)
WHERE _dedupe_rank = 1;

CREATE OR REFRESH MATERIALIZED VIEW quarantine_claims
COMMENT 'Every rejected claim row, its source file, rule and reason.'
AS
WITH all_claims AS (
  SELECT
    medClaimId AS claim_id,
    'MEDICAL' AS claim_channel,
    billingEntityName AS pharmacy_name,
    serviceFromDate AS service_date_raw,
    productCode AS product_code,
    rebateUnitsRequested AS rebate_units_raw,
    rebateAmount AS rebate_amount_raw,
    receivedTimestamp AS submitted_at_raw,
    _source_file,
    _ingested_at,
    to_json(named_struct(
      'medClaimId', medClaimId,
      'billingEntityName', billingEntityName,
      'billingNpi', billingNpi,
      'serviceFromDate', serviceFromDate,
      'productCode', productCode,
      'unitsBilled', unitsBilled,
      'rebateUnitsRequested', rebateUnitsRequested,
      'rebateAmount', rebateAmount,
      'entityAddress', entityAddress,
      'entityPhone', entityPhone,
      'entityFax', entityFax,
      'receivedTimestamp', receivedTimestamp
    )) AS raw_record
  FROM bronze_medical_claims
  UNION ALL
  SELECT
    RX_CLAIM_NBR,
    'PHARMACY',
    PHARMACY_NAME,
    FILL_DATE,
    PRODUCT_NDC,
    REBATE_UNITS,
    REBATE_AMT,
    SUBMISSION_TS,
    _source_file,
    _ingested_at,
    to_json(named_struct(
      'RX_CLAIM_NBR', RX_CLAIM_NBR,
      'PHARMACY_NAME', PHARMACY_NAME,
      'NCPDP_ID', NCPDP_ID,
      'FILL_DATE', FILL_DATE,
      'PRODUCT_NDC', PRODUCT_NDC,
      'QTY_DISPENSED', QTY_DISPENSED,
      'REBATE_UNITS', REBATE_UNITS,
      'REBATE_AMT', REBATE_AMT,
      'STORE_ADDR', STORE_ADDR,
      'PHONE_NBR', PHONE_NBR,
      'FAX_NBR', FAX_NBR,
      'SUBMISSION_TS', SUBMISSION_TS
    ))
  FROM bronze_pharmacy_claims
), classified AS (
  SELECT
    *,
    CASE
      WHEN coalesce(trim(claim_id), '') = '' THEN 'MISSING_CLAIM_ID'
      WHEN try_cast(rebate_units_raw AS DECIMAL(18, 2)) <= 0 THEN 'NON_POSITIVE_REBATE_UNITS'
      WHEN try_cast(service_date_raw AS DATE) IS NULL THEN 'INVALID_SERVICE_DATE'
      WHEN upper(trim(product_code)) NOT IN ('99999-0101-01', '99999-0102-01', '99999-0201-01', '99999-0301-01') THEN 'UNKNOWN_PRODUCT_CODE'
      ELSE NULL
    END AS invalid_reason,
    row_number() OVER (
      PARTITION BY claim_channel, raw_record
      ORDER BY _source_file, _ingested_at
    ) AS exact_row_number
  FROM all_claims
)
SELECT
  claim_id,
  claim_channel,
  pharmacy_name,
  service_date_raw,
  product_code,
  rebate_units_raw,
  rebate_amount_raw,
  submitted_at_raw,
  _source_file,
  _ingested_at,
  raw_record,
  coalesce(invalid_reason, 'EXACT_RETRANSMISSION') AS quarantine_reason
FROM classified
WHERE invalid_reason IS NOT NULL
   OR (invalid_reason IS NULL AND exact_row_number > 1);

CREATE OR REFRESH STREAMING TABLE silver_product_movement (
  movement_id STRING,
  movement_source STRING,
  source_entity_id STRING,
  pharmacy_name STRING,
  pharmacy_address STRING,
  phone STRING,
  fax STRING,
  product_code STRING,
  movement_date DATE,
  signed_units DECIMAL(18, 2),
  net_amount DECIMAL(18, 2),
  movement_type STRING,
  _source_file STRING,
  _ingested_at TIMESTAMP
)
COMMENT 'Conformed direct and wholesaler product movements.';

CREATE FLOW manufacturer_sales_flow AS INSERT INTO silver_product_movement BY NAME
SELECT
  trim(SALES_DOC_NBR) AS movement_id,
  'MANUFACTURER' AS movement_source,
  trim(SOLD_TO_ACCT) AS source_entity_id,
  trim(SHIP_TO_NAME) AS pharmacy_name,
  upper(trim(SHIP_TO_ADDR)) AS pharmacy_address,
  CAST(NULL AS STRING) AS phone,
  CAST(NULL AS STRING) AS fax,
  CASE upper(trim(MATERIAL_CD))
    WHEN 'CGM-SENSOR-01' THEN '99999-0101-01'
    WHEN 'CGM-SENSOR-02' THEN '99999-0102-01'
    WHEN 'CGM-READER-01' THEN '99999-0201-01'
    WHEN 'CGM-TRANSMIT-01' THEN '99999-0301-01'
  END AS product_code,
  try_cast(SHIP_DT AS DATE) AS movement_date,
  try_cast(QTY_SHIPPED AS DECIMAL(18, 2)) AS signed_units,
  try_cast(NET_AMT AS DECIMAL(18, 2)) AS net_amount,
  upper(trim(DOC_TYPE)) AS movement_type,
  _source_file,
  _ingested_at
FROM STREAM(bronze_manufacturer_sales);

CREATE FLOW wholesaler_shipments_flow AS INSERT INTO silver_product_movement BY NAME
SELECT
  trim(Transaction_ID) AS movement_id,
  'WHOLESALER' AS movement_source,
  trim(Wholesaler_Customer_ID) AS source_entity_id,
  trim(Customer_Name) AS pharmacy_name,
  upper(trim(Customer_Address)) AS pharmacy_address,
  regexp_replace(coalesce(Customer_Phone, ''), '[^0-9]', '') AS phone,
  regexp_replace(coalesce(Customer_Fax, ''), '[^0-9]', '') AS fax,
  upper(trim(NDC)) AS product_code,
  to_date(Invoice_Date, 'MM/dd/yyyy') AS movement_date,
  try_cast(
    CASE WHEN upper(trim(Transaction_Type)) = 'RETURN' THEN -1 ELSE 1 END
      * try_cast(Quantity AS DECIMAL(18, 2))
    AS DECIMAL(18, 2)
  ) AS signed_units,
  CAST(NULL AS DECIMAL(18, 2)) AS net_amount,
  upper(trim(Transaction_Type)) AS movement_type,
  _source_file,
  _ingested_at
FROM STREAM(bronze_wholesaler_shipments);

CREATE OR REFRESH MATERIALIZED VIEW silver_pharmacy_entities
COMMENT 'Latest source pharmacy identity linked to a stable canonical reference identifier.'
AS
WITH ranked_reference AS (
  SELECT
    sourceEntityId AS pharmacy_id,
    trim(legalName) AS legal_name,
    trim(doingBusinessAs) AS doing_business_as,
    upper(trim(address)) AS pharmacy_address,
    regexp_replace(coalesce(phone, ''), '[^0-9]', '') AS phone,
    regexp_replace(coalesce(fax, ''), '[^0-9]', '') AS fax,
    upper(trim(status)) AS entity_status,
    try_cast(effectiveDate AS DATE) AS effective_date,
    try_cast(closedDate AS DATE) AS closed_date,
    regexp_extract(_source_file, '/(\\d{4}-\\d{2})/', 1) AS snapshot_period,
    row_number() OVER (
      PARTITION BY sourceEntityId
      ORDER BY regexp_extract(_source_file, '/(\\d{4}-\\d{2})/', 1) DESC
    ) AS latest_rank
  FROM bronze_pharmacy_reference
)
SELECT * EXCEPT (latest_rank)
FROM ranked_reference
WHERE latest_rank = 1;
