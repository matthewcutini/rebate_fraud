# Databricks notebook source
import json
from datetime import timedelta

import psycopg
from databricks.sdk import WorkspaceClient


dbutils.widgets.text("catalog", "vandelay")
dbutils.widgets.text("schema", "rebate_fraud")
dbutils.widgets.text("endpoint", "")
dbutils.widgets.text("database", "databricks_postgres")
dbutils.widgets.text("app_name", "")
dbutils.widgets.text("genie_space_id", "")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
endpoint = dbutils.widgets.get("endpoint")
database = dbutils.widgets.get("database")
app_name = dbutils.widgets.get("app_name")
genie_space_id = dbutils.widgets.get("genie_space_id")

workspace = WorkspaceClient()

gold_row = spark.sql(
    f"""
    SELECT count(*) AS case_count, round(sum(estimated_overpayment), 2) AS exposure
    FROM {catalog}.{schema}.gold_fraud_cases
    """
).first()
governed_row = spark.sql(
    f"""
    SELECT count(DISTINCT case_id) AS case_count, round(sum(estimated_overpayment), 2) AS exposure
    FROM {catalog}.{schema}.governed_case_features
    """
).first()

endpoint_details = workspace.postgres.get_endpoint(name=endpoint)
credential = workspace.postgres.generate_database_credential(endpoint=endpoint)
with psycopg.connect(
    host=endpoint_details.status.hosts.host,
    port=5432,
    dbname=database,
    user=workspace.current_user.me().user_name,
    password=credential.token,
    sslmode="require",
) as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT count(*), round(sum(estimated_overpayment), 2) FROM rebate_ops.cases")
        lakebase_count, lakebase_exposure = cursor.fetchone()

app = workspace.apps.get(app_name)
postgres_resource = next(resource.postgres for resource in app.resources if resource.postgres is not None)

message = workspace.genie.start_conversation(
    genie_space_id,
    "How many suspected fraud cases exist, and what is their total estimated exposure?",
).result(timeout=timedelta(minutes=10))
query_attachment = next(attachment for attachment in message.attachments or [] if attachment.query is not None)
query_result = workspace.genie.get_message_attachment_query_result(
    genie_space_id,
    message.conversation_id,
    message.message_id,
    query_attachment.attachment_id,
)
genie_values = query_result.statement_response.result.data_array[0]

summary = {
    "gold_priority": {"case_count": int(gold_row.case_count), "exposure": str(gold_row.exposure)},
    "lakebase": {"case_count": int(lakebase_count), "exposure": str(lakebase_exposure)},
    "app": {
        "status": app.app_status.state.value,
        "deployment_status": app.active_deployment.status.state.value,
        "case_count": int(lakebase_count),
        "database": postgres_resource.database,
    },
    "governed_gold": {"case_count": int(governed_row.case_count), "exposure": str(governed_row.exposure)},
    "genie": {"case_count": int(genie_values[0]), "exposure": str(genie_values[1])},
    "genie_sql": query_attachment.query.query,
}

assert summary["gold_priority"] == summary["lakebase"]
assert summary["app"]["status"] == "RUNNING"
assert summary["app"]["deployment_status"] == "SUCCEEDED"
assert summary["app"]["case_count"] == summary["gold_priority"]["case_count"]
assert summary["genie"]["case_count"] == summary["governed_gold"]["case_count"]
assert float(summary["genie"]["exposure"]) == float(summary["governed_gold"]["exposure"])

dbutils.notebook.exit(json.dumps(summary))
