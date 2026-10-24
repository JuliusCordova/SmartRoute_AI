# Diagrama lógico relacional
```mermaid
erDiagram
 APP_USER ||--o| DRIVER : "perfil"
 APP_USER ||--o{ DELIVERY_ORDER : "registra"
 DRIVER ||--o{ DELIVERY_ROUTE : "asignado"
 DELIVERY_ROUTE ||--o{ ROUTE_STOP : "contiene"
 DELIVERY_ORDER ||--o| ROUTE_STOP : "asignada"
 DELIVERY_ORDER ||--o{ ORDER_STATUS_EVENT : "historial"
 DRIVER ||--o{ DRIVER_LOCATION : "reporta"
 DELIVERY_ROUTE ||--o{ ROUTE_EVALUATION : "mide"
 DELIVERY_ORDER ||--o{ INCIDENT : "reporta"
 APP_USER { uuid id PK string role bool active }
 DRIVER { uuid id PK uuid user_id FK bool gps_consent }
 DELIVERY_ORDER { uuid id PK string status float latitude float longitude }
 DELIVERY_ROUTE { uuid id PK uuid driver_id FK string status float depot_lat float depot_lon }
 ROUTE_STOP { uuid id PK uuid route_id FK uuid order_id FK int baseline_seq int optimized_seq }
 ORDER_STATUS_EVENT { uuid id PK uuid order_id FK string event_type string idempotency_key datetime occurred_at }
 DRIVER_LOCATION { uuid id PK uuid driver_id FK uuid route_id FK float lat float lon datetime captured_at }
 ROUTE_EVALUATION { uuid id PK uuid route_id FK float baseline_seconds float optimized_seconds string source_type string matrix_fingerprint }
 INCIDENT { uuid id PK uuid order_id FK string type datetime occurred_at }
```
DDL [schema.sql](../../db/schema.sql) se considera propuesta, no migración aplicada. Indexar eventos por ruta/tiempo, controlar claves únicas y política de retención GPS.
