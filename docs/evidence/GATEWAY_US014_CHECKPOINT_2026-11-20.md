# SmartRoute AI — Gateway US-012/013/014: paso 309

**Fecha:** 20-11-2026, Perú. **Rama:** `feat/mobile-driver-android-base`. **PR:** #56 draft, sin merge.

## Evidencia anterior, validada por el usuario

- Backend FastAPI y Firestore Emulator: **84 passed, 1 skipped, 8 warnings**.
- Imagen Artifact Registry `smartroute-api:us014-cc21fe7`, digest `sha256:fb46e00c5c5469fce1138efdda4634b2a1316668d8cf27c9a96c6c51b3a9955e`.
- Cloud Run API `smartroute-api-staging-00013-yev`, tag `us014-backend-test`, estado Ready/Healthy, **0 % tráfico principal**.
- API `GET /health` → HTTP 200; OpenAPI publica GET ruta propia y POST start/deliver/fail/complete; POST sin credenciales → HTTP 403.
- **100 % tráfico actual** API: `smartroute-api-staging-00010-juz`; gateway: `smartroute-gateway-staging-00011-quj`.
- Gateway etiquetado anterior `00013-sov` apunta al backend `us012-version-test`, no al nuevo tag.

## Cambios en GitHub realizados en el paso 309

- `services/gateway/app/main.py`: `APPROVED_API_URLS` con URLs exactas aprobadas, incluida API nueva `us014-backend-test`; `backend_url()` fail-closed si variable env difiere. El destino upstream del proxy se lee de ese allowlist; audiencia IAM token sigue siendo el **Cloud Run service URL canónico** `PRIVATE_API_URL`.
- Allowlist explícita para `POST /api/v1/driver/me/route/start` y `/complete` y patrón de `/stops/{order_id}/deliver` o `/fail`; control equivalente para CORS preflight.
- `services/gateway/tests/test_gateway_driver_workflow.py`: tests de autenticación Firebase, protección IAM, rechazo destinos externos, allowlist y separación de credenciales; sin red o cloud real.

**Estos tests aún NO han sido ejecutados en Cloud Shell**. No declarar gateway validado ni desplegado todavía.

## Próximo paso exacto

En Cloud Shell, con checkout del repositorio temporal `/tmp/smartroute-backend-qa`:

```bash
cd /tmp/smartroute-backend-qa
git pull --ff-only origin feat/mobile-driver-android-base
cd services/gateway
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q tests/
```

**Antes de construir**, revisar la nueva suite e introducir `services/gateway/.dockerignore` para excluir `.venv/` (contexto Docker), ya que el repositorio no tiene ese archivo todavía.

**Después de pruebas verdes:** construir imagen gateway etiquetada por SHA, desplegar nueva revisión `us014-gateway-test` con `--no-traffic` y `--update-env-vars SMARTROUTE_BACKEND_URL=https://us014-backend-test---smartroute-api-staging-mkqutd4koq-uc.a.run.app`, previa revisión de IAM y configuración de revisión. **No enviar tráfico principal ni cambiar gateway canonical.** Primero health y negativos sin mutación, luego E2E QA deliberado.

Conductor QA: `zMuwbYHLfST2QNdNkfosoCbUZ003`; ruta `21e3de4b-4002-5870-bc4e-8eafb2826219` PLANNED v2 según última evidencia (no consumir hasta acordar E2E). **Ruta Manuel `681f7f60-3a77-5f6b-975e-578fb03e4204` protegida.**

Android quedó en paso 288 (`adb devices` vacío), `ENABLE_DELIVERY_MUTATIONS=false`. No subir credenciales Firebase ni `google-services.json`.
