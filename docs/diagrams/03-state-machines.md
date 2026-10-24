# Estados e invariantes
```mermaid
stateDiagram-v2
 state "Pedidos" as Orders {
 [*] --> PENDING
 PENDING --> ASSIGNED: asignar
 ASSIGNED --> IN_TRANSIT: ruta activa
 IN_TRANSIT --> DELIVERED: completar
 IN_TRANSIT --> FAILED: incidencia
 }
 state "Rutas" as Routes {
 [*] --> DRAFT
 DRAFT --> PLANNED: optimizar
 PLANNED --> ACTIVE: publicar
 ACTIVE --> COMPLETED: cerrar
 DRAFT --> CANCELLED: cancelar
 PLANNED --> CANCELLED: cancelar
 }
```
Cada cambio de estado exige autorización, versión de entidad y evento idempotente. GPS sólo cuando ruta ACTIVE y consentimiento explícito vigente; al completar/cancelar se detiene. Se debe definir con negocio si FAILED admite reintento (fuera de v1).
