# Firestore Standard — modelo de documentos y operaciones

## Ejemplo sintético de pedido
```json
{
  "id": "synthetic-order-001",
  "created_by": "synthetic-operator",
  "address_label": "Destino sintético 1",
  "geo": {"lat": -12.09, "lng": -77.04},
  "status": "PENDING",
  "route_id": null,
  "version": 1,
  "data_origin": "synthetic",
  "created_at": "SERVER_TIMESTAMP"
}
```
No utilizar estas coordenadas como datos personales u observaciones reales. `SERVER_TIMESTAMP` es un marcador documental, no JSON válido para escribir sin transformación.

## Invariantes transaccionales
- `orders/{id}.route_id` ausente/NULL significa no asignado; la transacción lee y bloquea lógicamente la versión para impedir asignar el pedido en dos rutas.
- `order_events/{actorId}:{idempotencyKey}` se crea y actualiza `orders/{id}` dentro de una transacción. No ejecutar servicios externos dentro de la función transaccional.
- `routes/{id}.status` sólo puede recorrer DRAFT→PLANNED→ACTIVE→COMPLETED/CANCELLED según reglas; comprobar en servidor.
- No usar un único documento de eventos o contadores que concentre todas las escrituras.
- `driver_locations/{driverId}` representa última lectura, no historial completo; deshabilitar al terminar ruta, documentar borrado manual para evitar cargos por TTL.
- Crear índices compuestos **sólo** si una consulta real produce error que los necesite; registrar cada índice en `firestore.indexes.json`.

## Pruebas
1. `pytest` con mocks y Firestore Emulator para transacciones/idempotencia y asignación conflictiva; CI nunca utiliza proyecto real.
2. Test de autorización: usuario DRIVER no puede consultar todos los pedidos; una cuenta distinta no puede ver ruta ajena.
3. Verificar paginación y lecturas por una lista de 10 pedidos; registrar volumen.
4. Smoke autenticado contra staging con cuenta de servicio IAM mínima antes de promover.

## Fuentes
- https://firebase.google.com/docs/firestore/manage-data/transactions
- https://firebase.google.com/docs/firestore/security/insecure-rules
- https://cloud.google.com/firestore/pricing
