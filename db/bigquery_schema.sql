-- SmartRoute AI BigQuery schema for SMALL ACADEMIC PILOT ONLY.
-- Run: bq query --use_legacy_sql=false < db/bigquery_schema.sql
-- Uses dataset smartroute_mvp in configured GCP project/location.
-- UUIDs, status transitions, uniqueness and references are validated in FastAPI;
-- BigQuery does NOT enforce primary/foreign keys. Not an OLTP substitute.
CREATE SCHEMA IF NOT EXISTS `smartroute_mvp` OPTIONS(description="SmartRoute AI academic synthetic pilot");
CREATE TABLE IF NOT EXISTS `smartroute_mvp.app_users` (
 id STRING NOT NULL, email STRING NOT NULL, role STRING NOT NULL,
 active BOOL NOT NULL, created_at TIMESTAMP NOT NULL
) CLUSTER BY id;
CREATE TABLE IF NOT EXISTS `smartroute_mvp.drivers` (
 id STRING NOT NULL, user_id STRING NOT NULL, display_name STRING,
 gps_consent BOOL NOT NULL, consent_updated_at TIMESTAMP
) CLUSTER BY id;
CREATE TABLE IF NOT EXISTS `smartroute_mvp.delivery_orders` (
 id STRING NOT NULL, created_by STRING NOT NULL, address_label STRING NOT NULL,
 latitude FLOAT64 NOT NULL, longitude FLOAT64 NOT NULL,
 due_at TIMESTAMP, status STRING NOT NULL,
 created_at TIMESTAMP NOT NULL, updated_at TIMESTAMP NOT NULL,
 version INT64 NOT NULL
) CLUSTER BY id, status;
CREATE TABLE IF NOT EXISTS `smartroute_mvp.delivery_routes` (
 id STRING NOT NULL, driver_id STRING NOT NULL,
 depot_latitude FLOAT64 NOT NULL, depot_longitude FLOAT64 NOT NULL,
 status STRING NOT NULL, created_at TIMESTAMP NOT NULL,
 started_at TIMESTAMP, completed_at TIMESTAMP, version INT64 NOT NULL
) CLUSTER BY id, driver_id;
CREATE TABLE IF NOT EXISTS `smartroute_mvp.route_stops` (
 id STRING NOT NULL, route_id STRING NOT NULL, order_id STRING NOT NULL,
 baseline_sequence INT64 NOT NULL, optimized_sequence INT64,
 created_at TIMESTAMP NOT NULL
) CLUSTER BY route_id, order_id;
CREATE TABLE IF NOT EXISTS `smartroute_mvp.order_status_events` (
 event_id STRING NOT NULL, order_id STRING NOT NULL, actor_id STRING NOT NULL,
 old_status STRING, new_status STRING NOT NULL,
 idempotency_key STRING NOT NULL, occurred_at TIMESTAMP NOT NULL,
 received_at TIMESTAMP NOT NULL, data_origin STRING NOT NULL
) PARTITION BY DATE(received_at) CLUSTER BY order_id, idempotency_key
 OPTIONS(require_partition_filter=TRUE);
CREATE TABLE IF NOT EXISTS `smartroute_mvp.driver_locations` (
 location_id STRING NOT NULL, driver_id STRING NOT NULL, route_id STRING NOT NULL,
 latitude FLOAT64 NOT NULL, longitude FLOAT64 NOT NULL,
 accuracy_m FLOAT64, captured_at TIMESTAMP NOT NULL,
 received_at TIMESTAMP NOT NULL, data_origin STRING NOT NULL
) PARTITION BY DATE(received_at) CLUSTER BY driver_id, route_id
 OPTIONS(require_partition_filter=TRUE);
CREATE TABLE IF NOT EXISTS `smartroute_mvp.route_evaluations` (
 id STRING NOT NULL, route_id STRING NOT NULL,
 baseline_seconds INT64 NOT NULL, optimized_seconds INT64 NOT NULL,
 matrix_fingerprint STRING NOT NULL, matrix_source STRING NOT NULL,
 data_origin STRING NOT NULL, solver_version STRING NOT NULL,
 calculated_at TIMESTAMP NOT NULL
) CLUSTER BY route_id;
CREATE TABLE IF NOT EXISTS `smartroute_mvp.incidents` (
 id STRING NOT NULL, order_id STRING NOT NULL,
 incident_type STRING NOT NULL, description STRING,
 created_at TIMESTAMP NOT NULL
) CLUSTER BY order_id;
-- Do not assume an append to events is exactly-once.
-- For a pilot, serialize conflicting writes in a single API worker and reconcile.
-- This is an operational limitation, not a general distributed guarantee.
