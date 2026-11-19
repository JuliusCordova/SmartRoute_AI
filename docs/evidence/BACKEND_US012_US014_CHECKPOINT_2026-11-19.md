# SmartRoute AI — Checkpoint backend US-012 + US-013 + US-014

**Fecha:** 19-11-2026, Perú. **Objetivo:** continuidad mañana desde un bloque de backend listo para probar, **sin desplegar**.

## 1. Estado y alcance

Implementación propuesta en la rama `feat/mobile-driver-android-base` / PR [#56](https://github.com/JuliusCordova/SmartRoute_AI/pull/56) (draft, sin merge).

- **US-012**: `POST /api/v1/driver/me/route/start` → `PLANNED → ACTIVE`, todos los pedidos `ASSIGNED → IN_TRANSIT`, ocupación `RESERVED → ACTIVE`, versión +1.
- **US-013**: `POST /api/v1/driver/me/route/stops/{order_id}/deliver` → `IN_TRANSIT → DELIVERED`; `POST .../fail` → `IN_TRANSIT → FAILED` con motivo obligatorio; versión de ruta +1 y versión de pedido +1.
- **US-014**: `POST /api/v1/driver/me/route/complete` → `ACTIVE → COMPLETED` solo si todas las paradas son `DELIVERED` o `FAILED`, resumen final, liberación de conductor y eliminación de reserva.
- **GET** `/api/v1/driver/me/route`: proyección por Firebase UID con `stops[].status`, compatible con Android, y lectura del último recorrido completado por `driver_last_routes/{uid}` cuando no hay reserva activa.
- **Seguridad**: autorización `require_driver` del backend, sin UID en payload, todas las operaciones usan transacción de Firestore sobre la base configurada `smartroute`.
- **Idempotencia**: documento `driver_route_events/{sha256(uid:route_id:key)}` creado en la misma transacción, fingerprint de operación y recibo; clave repetida con payload diferente => conflicto; versión optimista bloquea estados desactualizados.
- **Sin tráfico de producción ni GCP mutado**: los commits solo afectan GitHub. La base `(default)` y `gestioncitas` siguen protegidas fuera de emulador por `firestore_config.py`.

### Código y pruebas agregados

| Archivo | Contenido |
|---|---|
| `services/api/app/driver_workflow.py` | Contratos Pydantic de mutación y recibos |
| `services/api/app/firestore_driver_workflow.py` | Transacciones y eventos Firestore |
| `services/api/app/main.py` | Cuatro rutas HTTP DRIVER |
| `services/api/app/driver_assignment.py` | Estados por parada y estado `COMPLETED` |
| `services/api/app/firestore_driver_assignment.py` | Lectura de estados autoritativos e historial de última ruta |
| `services/api/tests/test_driver_workflow_api.py` | Tests FastAPI de autenticación, payloads, errores y respuestas |
| `services/api/tests/test_driver_workflow_firestore_emulator.py` | E2E sintético con Firestore Emulator; no corre contra GCP real |

**Limitación de evidencia:** las pruebas se han **añadido al repositorio, pero no hay ejecución verde confirmada de este nuevo backend** en el momento del checkpoint. No etiquetar US-012/013/014 como aceptadas sin tests e integración.

## 2. API que espera Android

Todos los POST requieren `Authorization: Bearer <Firebase ID token>` y `Content-Type: application/json`; autenticación con usuario `DRIVER` activo:

```http
POST /api/v1/driver/me/route/start
{"expected_version":2,"idempotency_key":"<UUID>"}
# 200 {"id":"<route-id>","status":"ACTIVE","version":3}
```

```http
POST /api/v1/driver/me/route/stops/{order_id}/deliver
{"expected_version":3,"idempotency_key":"<UUID>"}
# 200 {"id":"<route-id>","status":"ACTIVE","version":4,
#      "order_id":"<order-id>","order_status":"DELIVERED"}
```

```http
POST /api/v1/driver/me/route/stops/{order_id}/fail
{"expected_version":4,"idempotency_key":"<UUID>","reason":"Local cerrado"}
# 200 {"id":"<route-id>","status":"ACTIVE","version":5,
#      "order_id":"<order-id>","order_status":"FAILED"}
```

```http
POST /api/v1/driver/me/route/complete
{"expected_version":N,"idempotency_key":"<UUID>"}
# 200 {"id":"<route-id>","status":"COMPLETED","version":N+1}
```

Errores: `401` sin credencial, `403` rol inválido, `404` parada/ruta no encontrada, `409` versión/conflicto, `422` payload inválido, `503` error de almacenamiento. El GET de ruta es `200` (incluye `stops[].status`) o `204` sin ruta ni historial.

## 3. Pruebas que debe ejecutar el compañero antes de desplegar

En Cloud Shell o entorno Python aislado:

```bash
cd ~/SmartRoute_AI
git fetch origin
git switch feat/mobile-driver-android-base
git pull --ff-only origin feat/mobile-driver-android-base
cd services/api
source .venv/bin/activate
python -m pytest -q tests/test_driver_workflow_api.py tests/test_driver_own_route_api.py tests/test_driver_assignment_contract.py
python -m pytest -q
```

**No usar credenciales de servicio de producción para estas pruebas.** Para pruebas transaccionales, conectar `FIRESTORE_EMULATOR_HOST` a Firestore Emulator y ejecutar:

```bash
FIRESTORE_EMULATOR_REQUIRED=1 python -m pytest -q tests/test_driver_workflow_firestore_emulator.py
```

Si no existe emulador, el test falla de forma segura con el flag `FIRESTORE_EMULATOR_REQUIRED=1`, sin tocar GCP. Verificar especialmente transacciones reales, idempotencia tras cierre, rechazo de cierre prematuro, estado de reservas, `driver_last_routes`, eventos y versiones.

**Antes del piloto:** comparar OpenAPI del servicio desplegado y la rama, confirmar IAM de gateway/API, ejecutar revisión etiquetada sin enrutar tráfico principal. No activar `AppConfig.ENABLE_DELIVERY_MUTATIONS = true` hasta verificar el E2E con conductor QA, y no tocar la ruta del piloto Manuel.

## 4. Datos QA reservados (NO ejecutar aún mutaciones reales)

- GCP: `proyectopersonal-480420`, Firestore **`smartroute`**.
- Conductor QA: `zMuwbYHLfST2QNdNkfosoCbUZ003`.
- Ruta: `21e3de4b-4002-5870-bc4e-8eafb2826219`, 6 órdenes sintéticas, `PLANNED`, versión 2; `driver_assignments` `RESERVED`, versión 1 (última evidencia).
- Conductor Manuel: ruta `681f7f60-3a77-5f6b-975e-578fb03e4204`, **no intervenir**.
- El usuario dejó Android pausado en **paso 288: iniciar emulador en Android Studio; ADB instalado pero `adb devices` vacío**.

## 5. Punto de reanudación mañana

**Prioridad inmediata:** ejecutar pytest del nuevo backend y test de Firestore Emulator, corregir cualquier fallo y volver a verificar `main.py` / `DriverRoute`. Luego comprobar paso 288 Android y preparar despliegue etiquetado de backend para QA, sin mutar la ruta Manuel ni el tráfico principal.

**Criterio de aceptación:** API tests + emulador verdes, E2E Android QA de inicio/entrega/cierre, eventos y versiones verificadas antes de solicitar merge PR #56.
