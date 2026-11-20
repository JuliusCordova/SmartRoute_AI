# SmartRoute AI — Validación backend US-012/013/014 — 20 noviembre 2026

## Evidencia suministrada por el equipo

Cloud Shell, repositorio temporal `/tmp/smartroute-backend-qa`, rama `feat/mobile-driver-android-base` (commit descargado `bc689b1` antes de generar este documento), directorio `services/api`, Python 3.12.3, entorno virtual `.venv`.

```bash
export FIRESTORE_EMULATOR_HOST=127.0.0.1:8085
export GOOGLE_CLOUD_PROJECT=demo-smartroute
export FIRESTORE_EMULATOR_REQUIRED=1
python -m pytest -q
```

Salida reportada por el usuario el 20-11-2026:

```text
84 passed, 1 skipped, 8 warnings in 6.04s
```

El comando `curl` a `http://127.0.0.1:8085/` respondió `200`. El intento de reiniciar el emulador devolvió un trabajo de shell terminado inmediatamente, pero las pruebas se ejecutaron y aprobaron con un servicio accesible en el puerto 8085. Para próximas sesiones verificar PID/puerto y no asumir que el segundo arranque quedó activo.

## Historias cubiertas por las pruebas automáticas

- US-012 — iniciar ruta `PLANNED → ACTIVE`, pedidos `ASSIGNED → IN_TRANSIT`.
- US-013 — registrar `DELIVERED` y `FAILED` con motivo.
- US-014 — impedir cierre con pendientes, cerrar en `COMPLETED`, liberar reserva, mantener resumen y consulta de último recorrido.
- Control de versiones, idempotencia y rechazo de operaciones obsoletas o duplicadas.
- Regresión: pedidos, optimización, rutas y asignación de conductores.

## Advertencias observadas (no bloqueantes)

1. `StarletteDeprecationWarning`: compatibilidad futura de `httpx` con `starlette.testclient`.
2. Pydantic: test de asignación inserta string `ASSIGNED` en lugar del enum al serializar `Order` (en cinco pruebas).
3. Firestore: uso de filtros posicionales en dos pruebas.

No se ha realizado un análisis de cobertura porcentual; `84 passed` no equivale a validación en producción.

## Estado de despliegue y controles

- Código en PR [#56](https://github.com/JuliusCordova/SmartRoute_AI/pull/56), rama `feat/mobile-driver-android-base`, **sin merge**.
- No se ha desplegado la nueva implementación de FastAPI US-012/013/014 en Cloud Run.
- No se ha habilitado `ENABLE_DELIVERY_MUTATIONS=true` en Android.
- No se han modificado datos de Firestore real `smartroute` durante estas pruebas.
- Proyecto real GCP: `proyectopersonal-480420`. La base `(default)` y `gestioncitas` están protegidas por la configuración fail-closed.
- Ruta del conductor Manuel `681f7f60-3a77-5f6b-975e-578fb03e4204`: **no tocar**.
- Ruta sintética QA `21e3de4b-4002-5870-bc4e-8eafb2826219`, `PLANNED`, versión 2 según la última evidencia; no iniciar hasta preparar despliegue y validación controlada.

## Próximo paso

**Paso 297:** confirmar fuente, IAM y configuración del gateway privado y la API; verificar cuál es la versión desplegada antes de crear una revisión etiquetada de Cloud Run SIN ENVIAR TRÁFICO PRINCIPAL. Continuar con pruebas autenticadas en staging aislado. Solo después probar Android en el emulador (paso 288 quedó pendiente: `adb devices` sin dispositivos).

Pendientes para hardening: resolver advertencias, pruebas de concurrencia/errores de red, validar contratos Android-backend en ambiente desplegado, trazabilidad de eventos, monitoreo y criterios de cierre/merge.
