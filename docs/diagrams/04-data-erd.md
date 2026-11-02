# Modelo lógico adaptado a BigQuery (piloto, no ERD transaccional)
```mermaid
erDiagram
 APP_USERS ||--o| DRIVERS : "logical_user_id"
 APP_USERS ||--o{ DELIVERY_ORDERS : "created_by"
 DRIVERS ||--o{ DELIVERY_ROUTES : "driver_id"
 DELIVERY_ROUTES ||--o{ ROUTE_STOPS : "route_id"
 DELIVERY_ORDERS ||--o{ ROUTE_STOPS : "order_id"
 DELIVERY_ORDERS ||--o{ ORDER_STATUS_EVENTS : "order_id"
 DRIVERS ||--o{ DRIVER_LOCATIONS : "driver_id"
 DELIVERY_ROUTES ||--o{ ROUTE_EVALUATIONS : "route_id"
 DELIVERY_ORDERS ||--o{ INCIDENTS : "order_id"
 APP_USERS { string id string email string role bool active }
 DRIVERS { string id string user_id bool gps_consent }
 DELIVERY_ORDERS { string id string status float latitude float longitude int version }
 DELIVERY_ROUTES { string id string driver_id string status int version }
 ROUTE_STOPS { string id string route_id string order_id int baseline_sequence int optimized_sequence }
 ORDER_STATUS_EVENTS { string event_id string order_id string idempotency_key datetime received_at }
 DRIVER_LOCATIONS { string location_id string driver_id string route_id datetime received_at }
 ROUTE_EVALUATIONS { string id string route_id string data_origin int baseline_seconds int optimized_seconds }
 INCIDENTS { string id string order_id string incident_type }
```
**Atención:** las relaciones representan referencias lógicas, NO claves foráneas impuestas por BigQuery. Los controles de asignación, estado e idempotencia pertenecen a FastAPI y deben pasar pruebas. DDL vigente: [bigquery_schema.sql](../../db/bigquery_schema.sql). PostgreSQL histórico: [schema.sql](../../db/schema.sql), no ejecutarlo en GCP.
