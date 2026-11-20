# SmartRoute AI — checkpoint suite completa Firestore Emulator (20-11-2026)

## Resultado comprobado antes de correcciones
- `python -m pytest -q` con `FIRESTORE_EMULATOR_HOST=127.0.0.1:8085`, `GOOGLE_CLOUD_PROJECT=demo-smartroute`, `FIRESTORE_EMULATOR_REQUIRED=1`: **81 passed, 3 failed, 1 skipped, 3 warnings**.
- `tests/test_driver_assignment_emulator.py::test_own_route_read_is_scoped_to_driver_uid`: el fixture creaba pedido parcial sin `status`, y `own_route` exige ahora estado autorizado de cada parada.
- `tests/test_firestore_integration.py::test_create_and_page_against_firestore_emulator`: contaminación del emulador compartido por documento `orders/order-1` parcial de la prueba previa.
- `tests/test_optimized_routes_emulator.py::test_atomic_save_reserves_orders_and_retries`: contaminación del emulador por ruta US-012/013/014 parcial de prueba workflow; modelo `OptimizedRoute` solo aceptaba `PLANNED`.

## Correcciones versionadas en PR #56
1. `services/api/tests/test_driver_assignment_emulator.py`: fixture crea pedido con esquema completo `new_order()`, ID UUID exclusivo por escenario; elimina `orders/order-1` compartido y las escrituras parciales.
2. `services/api/tests/test_driver_workflow_firestore_emulator.py`: fixture usa `OptimizedRoute` con campos completos y órdenes completas `new_order()`, conserva comprobaciones de transacciones, idempotencia, estados y auditoría.
3. `services/api/app/optimized_routes.py`: `OptimizedRoute.status` acepta `PLANNED`, `ACTIVE`, `COMPLETED`, `CANCELLED` para que las lecturas de rutas finalizadas no fallen con el ciclo de vida real.

**Estas correcciones todavía necesitan re-ejecutarse en Cloud Shell; no afirmar que el conjunto está verde.**

## Paso siguiente
Reiniciar **solo** el Firestore Emulator local para eliminar documentos sintéticos parciales de las pruebas anteriores; luego descargar la rama con `git pull --ff-only`, activar exclusivamente emulador y repetir la suite completa.

```bash
cd /tmp/smartroute-backend-qa/services/api
git pull --ff-only origin feat/mobile-driver-android-base
# Parar el emulador local previo; después reiniciarlo con JAVA_HOME Java 25 y puerto 8085.
export FIRESTORE_EMULATOR_HOST=127.0.0.1:8085
export GOOGLE_CLOUD_PROJECT=demo-smartroute
export FIRESTORE_EMULATOR_REQUIRED=1
python -m pytest -q
```

**No se ha desplegado Cloud Run, no se ha modificado Firestore `smartroute` ni la ruta de Manuel, y PR #56 sigue draft sin merge.**
