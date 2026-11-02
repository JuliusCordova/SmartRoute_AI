# Modelo lógico — Firestore Standard (documentos, no tablas)
```mermaid
flowchart TD
  U["users/{uid} · rol / active"]
  D["drivers/{driverId} · user_id / gps_consent"]
  O["orders/{orderId} · status / route_id / geo"]
  R["routes/{routeId} · driver_id / status / sequence"]
  S["routes/{routeId}/stops/{orderId}"]
  E["order_events/{actorId}:{key} · idempotencia"]
  GPS["driver_locations/{driverId} · último GPS"]
  RE["route_evaluations/{id}"]
  IN["incidents/{id}"]
  U --> D
  D --> R
  R --> S
  O --> S
  O --> E
  D --> GPS
  R --> RE
  O --> IN
```
**Referencias lógicas gestionadas por FastAPI**. Firestore no impone claves foráneas ni cascadas relacionales. Las transacciones coordinan asignaciones, eventos y estados. Ver [colecciones](../FIRESTORE_COLLECTIONS.md) y [ADR vigente](../FIRESTORE_STANDARD_MVP.md).
