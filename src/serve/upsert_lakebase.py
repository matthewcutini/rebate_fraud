# Databricks notebook source
import json
from decimal import Decimal

import psycopg
from databricks.sdk import WorkspaceClient
from psycopg.types.json import Jsonb


dbutils.widgets.text("catalog", "vandelay")
dbutils.widgets.text("schema", "rebate_fraud")
dbutils.widgets.text("endpoint", "")
dbutils.widgets.text("database", "databricks_postgres")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
endpoint_path = dbutils.widgets.get("endpoint")
database_name = dbutils.widgets.get("database")

workspace = WorkspaceClient()


def connect():
    endpoint = workspace.postgres.get_endpoint(endpoint_path)
    credential = workspace.postgres.generate_database_credential(endpoint=endpoint_path)
    return psycopg.connect(
        host=endpoint.status.hosts.host,
        dbname=database_name,
        user=workspace.current_user.me().user_name,
        password=credential.token,
        sslmode="require",
    )


ddl = """
CREATE SCHEMA IF NOT EXISTS rebate_ops;

CREATE TABLE IF NOT EXISTS rebate_ops.cases (
  case_id text PRIMARY KEY,
  pharmacy_id text NOT NULL,
  pharmacy_name text NOT NULL,
  entity_status text,
  region text NOT NULL,
  state_code text NOT NULL,
  product_code text NOT NULL,
  review_period text NOT NULL,
  claim_count bigint NOT NULL,
  medical_claim_count bigint NOT NULL,
  pharmacy_claim_count bigint NOT NULL,
  source_identity_count bigint NOT NULL,
  claimed_units numeric(28, 2) NOT NULL,
  supported_units numeric(28, 2) NOT NULL,
  excess_units numeric(29, 2) NOT NULL,
  estimated_overpayment numeric(38, 6) NOT NULL,
  has_cross_channel_activity boolean NOT NULL,
  matched_cross_channel_pairs bigint NOT NULL,
  has_multiple_source_identities boolean NOT NULL,
  fraud_score integer NOT NULL CHECK (fraud_score BETWEEN 0 AND 100),
  score_drivers jsonb NOT NULL,
  period_rank integer NOT NULL,
  score_version text NOT NULL,
  ai_explanation text,
  ai_next_action text,
  ai_likely_explanation text,
  ai_model text,
  prompt_version text,
  source_scored_at timestamp,
  source_explained_at timestamp,
  source_refreshed_at timestamptz NOT NULL DEFAULT now(),
  status text NOT NULL DEFAULT 'NEW'
    CHECK (status IN ('NEW', 'IN_REVIEW', 'OUTREACH_SENT', 'VERIFIED', 'DISMISSED', 'ESCALATED', 'CLOSED')),
  owner text,
  priority text NOT NULL DEFAULT 'MEDIUM'
    CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')),
  notes text,
  due_date date,
  decision text,
  verified_fraud boolean,
  recovery_amount numeric(18, 2) CHECK (recovery_amount IS NULL OR recovery_amount >= 0),
  legal_escalation boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rebate_ops.case_events (
  event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  case_id text NOT NULL REFERENCES rebate_ops.cases(case_id),
  event_type text NOT NULL CHECK (event_type IN ('INSERT', 'UPDATE')),
  change_source text NOT NULL CHECK (change_source IN ('SYNC', 'APP', 'PSQL')),
  changed_by text NOT NULL,
  changed_at timestamptz NOT NULL DEFAULT now(),
  changed_columns text[] NOT NULL,
  before_state jsonb,
  after_state jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS rebate_ops.case_communications (
  communication_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  case_id text NOT NULL REFERENCES rebate_ops.cases(case_id),
  direction text NOT NULL CHECK (direction IN ('OUTBOUND', 'INBOUND')),
  channel text NOT NULL CHECK (channel IN ('EMAIL', 'PHONE', 'FAX', 'PORTAL')),
  subject text,
  body text NOT NULL,
  occurred_at timestamptz NOT NULL DEFAULT now(),
  recorded_by text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rebate_ops.sync_state (
  sync_name text PRIMARY KEY,
  source_table text NOT NULL,
  source_row_count bigint NOT NULL,
  inserted_count bigint NOT NULL,
  updated_count bigint NOT NULL,
  completed_at timestamptz NOT NULL,
  status text NOT NULL CHECK (status IN ('SUCCEEDED', 'FAILED'))
);

CREATE OR REPLACE FUNCTION rebate_ops.record_case_change()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  columns_changed text[];
  configured_source text;
  configured_actor text;
BEGIN
  configured_source := COALESCE(NULLIF(current_setting('rebate_ops.change_source', true), ''), 'PSQL');
  configured_actor := COALESCE(NULLIF(current_setting('rebate_ops.changed_by', true), ''), session_user);

  IF TG_OP = 'INSERT' THEN
    columns_changed := ARRAY(SELECT jsonb_object_keys(to_jsonb(NEW)) ORDER BY 1);
  ELSE
    SELECT array_agg(new_values.key ORDER BY new_values.key)
    INTO columns_changed
    FROM jsonb_each(to_jsonb(NEW)) AS new_values
    WHERE to_jsonb(OLD) -> new_values.key IS DISTINCT FROM new_values.value;
  END IF;

  INSERT INTO rebate_ops.case_events (
    case_id, event_type, change_source, changed_by, changed_columns, before_state, after_state
  ) VALUES (
    NEW.case_id,
    TG_OP,
    configured_source,
    configured_actor,
    columns_changed,
    CASE WHEN TG_OP = 'UPDATE' THEN to_jsonb(OLD) ELSE NULL END,
    to_jsonb(NEW)
  );
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS cases_change_history ON rebate_ops.cases;
CREATE TRIGGER cases_change_history
AFTER INSERT OR UPDATE ON rebate_ops.cases
FOR EACH ROW EXECUTE FUNCTION rebate_ops.record_case_change();

CREATE INDEX IF NOT EXISTS cases_status_due_date_idx ON rebate_ops.cases(status, due_date);
CREATE INDEX IF NOT EXISTS case_events_case_time_idx ON rebate_ops.case_events(case_id, changed_at DESC);
"""

source_columns = [
    "case_id",
    "pharmacy_id",
    "pharmacy_name",
    "entity_status",
    "region",
    "state_code",
    "product_code",
    "review_period",
    "claim_count",
    "medical_claim_count",
    "pharmacy_claim_count",
    "source_identity_count",
    "claimed_units",
    "supported_units",
    "excess_units",
    "estimated_overpayment",
    "has_cross_channel_activity",
    "matched_cross_channel_pairs",
    "has_multiple_source_identities",
    "fraud_score",
    "score_drivers",
    "period_rank",
    "score_version",
    "ai_explanation",
    "ai_next_action",
    "ai_likely_explanation",
    "ai_model",
    "prompt_version",
    "scored_at",
    "explained_at",
]

source_rows = spark.table(f"{catalog}.{schema}.gold_fraud_cases").select(*source_columns).collect()


def postgres_value(column, value):
    if column == "score_drivers":
        return Jsonb(value or [])
    if isinstance(value, Decimal):
        return value
    return value


records = [tuple(postgres_value(column, row[column]) for column in source_columns) for row in source_rows]

insert_columns = [
    "case_id",
    "pharmacy_id",
    "pharmacy_name",
    "entity_status",
    "region",
    "state_code",
    "product_code",
    "review_period",
    "claim_count",
    "medical_claim_count",
    "pharmacy_claim_count",
    "source_identity_count",
    "claimed_units",
    "supported_units",
    "excess_units",
    "estimated_overpayment",
    "has_cross_channel_activity",
    "matched_cross_channel_pairs",
    "has_multiple_source_identities",
    "fraud_score",
    "score_drivers",
    "period_rank",
    "score_version",
    "ai_explanation",
    "ai_next_action",
    "ai_likely_explanation",
    "ai_model",
    "prompt_version",
    "source_scored_at",
    "source_explained_at",
]

machine_columns = [column for column in insert_columns if column != "case_id"]
assignments = ",\n  ".join(f"{column} = EXCLUDED.{column}" for column in machine_columns)
distinct_left = ", ".join(f"cases.{column}" for column in machine_columns)
distinct_right = ", ".join(f"EXCLUDED.{column}" for column in machine_columns)
placeholders = ", ".join(["%s"] * len(insert_columns))

upsert_sql = f"""
INSERT INTO rebate_ops.cases ({', '.join(insert_columns)})
VALUES ({placeholders})
ON CONFLICT (case_id) DO UPDATE SET
  {assignments},
  source_refreshed_at = now(),
  updated_at = now()
WHERE ({distinct_left}) IS DISTINCT FROM ({distinct_right})
"""

with connect() as connection:
    with connection.cursor() as cursor:
        cursor.execute(ddl)
        cursor.execute("SET LOCAL rebate_ops.change_source = 'SYNC'")
        cursor.execute(
            "SELECT set_config('rebate_ops.changed_by', %s, true)",
            (workspace.current_user.me().user_name,),
        )
        cursor.execute("SELECT count(*) FROM rebate_ops.cases")
        before_count = cursor.fetchone()[0]
        cursor.executemany(upsert_sql, records)
        affected_count = cursor.rowcount
        cursor.execute("SELECT count(*) FROM rebate_ops.cases")
        after_count = cursor.fetchone()[0]
        inserted_count = max(after_count - before_count, 0)
        cursor.execute(
            """
            INSERT INTO rebate_ops.sync_state (
              sync_name, source_table, source_row_count, inserted_count, updated_count, completed_at, status
            ) VALUES ('gold_fraud_cases', %s, %s, %s, %s, now(), 'SUCCEEDED')
            ON CONFLICT (sync_name) DO UPDATE SET
              source_table = EXCLUDED.source_table,
              source_row_count = EXCLUDED.source_row_count,
              inserted_count = EXCLUDED.inserted_count,
              updated_count = EXCLUDED.updated_count,
              completed_at = EXCLUDED.completed_at,
              status = EXCLUDED.status
            """,
            (
                f"{catalog}.{schema}.gold_fraud_cases",
                len(records),
                inserted_count,
                max(affected_count - inserted_count, 0),
            ),
        )
        cursor.execute("SELECT count(*) FROM rebate_ops.case_events")
        event_count = cursor.fetchone()[0]

summary = {
    "source_rows": len(records),
    "case_rows": after_count,
    "inserted_rows": inserted_count,
    "history_rows": event_count,
    "endpoint": endpoint_path,
}
print(json.dumps(summary, default=str))
dbutils.notebook.exit(json.dumps(summary, default=str))
