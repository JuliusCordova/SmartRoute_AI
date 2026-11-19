# SmartRoute AI — Backend US-012/US-013/US-014: checkpoint para retomar

**Fecha:** 2026-11-19 (Lima). **Estado:** implementación backend publicada en rama de trabajo, **pendiente de pruebas y despliegue**.

El código de FastAPI y Firestore fue actualizado en [`feat/mobile-driver-android-base`](https://github.com/JuliusCordova/SmartRoute_AI/tree/feat/mobile-driver-android-base/services/api), PR [#56](https://github.com/JuliusCordova/SmartRoute_AI/pull/56) (draft, sin merge).

**Ver registro técnico completo en la rama:** [BACKEND_US012_US014_CHECKPOINT_2026-11-19.md](https://github.com/JuliusCordova/SmartRoute_AI/blob/feat/mobile-driver-android-base/docs/evidence/BACKEND_US012_US014_CHECKPOINT_2026-11-19.md).

## Código implementado

1. `services/api/app/driver_workflow.py`: DTO Pydantic `WorkflowRequest`, `StopResultRequest`, `RouteReceipt`, `StopReceipt`.
2. `services/api/app/firestore_driver_workflow.py`: ejecución en transacción Firestore, control de versión, idempotencia y eventos; inicio de recorrido, entrega exitosa, fallo con motivo y cierre.
3. `services/api/app/main.py`: cuatro POST DRIVER autenticados:
   - `/api/v1/driver/me/route/start`
   - `/api/v1/driver/me/route/stops/{order_id}/deliver`
   - `/api/v1/driver/me/route/stops/{order_id}/fail`
   - `/api/v1/driver/me/route/complete`.
4. `services/api/app/driver_assignment.py` y `firestore_driver_assignment.py`: consulta de ruta con `stops[].status`, soporte `COMPLETED` y lectura del último recorrido cerrado cuando ya no existe reserva.
5. `services/api/tests/test_driver_workflow_api.py`: pruebas de endpoints, acceso DRIVER, validación y mapeo de errores.
6. `services/api/tests/test_driver_workflow_firestore_emulator.py`: integración de Firestore Emulator sobre datos enteramente sintéticos, revisa transición `PLANNED→ACTIVE→COMPLETED`, dos resultados de paradas, reserva, versiones, eventos e idempotencia.

## Estado probado vs. pendiente

- **Implementado y versionado:** sí, código y tests añadidos al PR #56.
- **Pytest del backend tras el cambio:** **sin resultado de ejecución confirmado todavía**. No afirmar PASS.
- **Firestore Emulator:** test preparado, **no ejecutado aún**. Debe usarse `FIRESTORE_EMULATOR_HOST`; nunca Firestore live.
- **Despliegue etiquetado Cloud Run:** **no ejecutado**.
- **Activación de entregas reales en Android:** **bloqueada intencionalmente** con `ENABLE_DELIVERY_MUTATIONS=false`.
- **Merge de PR #56:** **no realizado**.
- **Modificaciones a Firestore GCP:** **ninguna en esta etapa**.

## Punto exacto mañana

1. En Cloud Shell: `git fetch origin && git switch feat/mobile-driver-android-base && git pull --ff-only origin feat/mobile-driver-android-base`.
2. `cd services/api && source .venv/bin/activate && python -m pytest -q tests/test_driver_workflow_api.py tests/test_driver_own_route_api.py tests/test_driver_assignment_contract.py`.
3. Ejecutar test transaccional en Firestore Emulator; no usar credenciales o base GCP real. Corregir eventuales fallos antes de desplegar.
4. Luego comprobar staging en revisión etiquetada, sin tráfico principal; mantener intacta la ruta de Manuel.
5. Android quedó en paso 288, sin emulador encendido (`adb devices` vacío). La ruta QA real `21e3de4b-4002-5870-bc4e-8eafb2826219` continúa `PLANNED`, versión 2, según última evidencia; no iniciar hasta tests seguros.

**Proyecto GCP:** `proyectopersonal-480420`; usar únicamente Firestore nombrado `smartroute`, nunca `(default)` o `gestioncitas`. **Conductor QA:** `zMuwbYHLfST2QNdNkfosoCbUZ003`.
