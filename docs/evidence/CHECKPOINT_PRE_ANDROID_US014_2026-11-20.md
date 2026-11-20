# SmartRoute AI — Corte previo a pruebas Android (20-11-2026)

**Estado:** checkpoint de continuidad. **No iniciar aún pruebas interactivas en Android ni ejecutar escrituras reales.**

## Versionado y ramas
- Repositorio: `JuliusCordova/SmartRoute_AI`
- Rama activa: `feat/mobile-driver-android-base`; PR **#56** permanece draft, **sin merge**.
- Último commit de código verificado tanto en GitHub como en Windows y Cloud Shell antes de este documento: `5b3f7fe` — `feat(android): conectar conductor al gateway US014 de staging`.
- Windows: `D:\Desarrollo\SmartRoute_AI_US012`; `git pull --ff-only` realizado exitosamente de `ff0bb69` a `5b3f7fe`. `git status --short` vacío; `git stash list` vacío.
- Cloud Shell: `$HOME/smartroute-backend-qa`; permanece `services/gateway/.venv/` sin seguimiento, **no subir**. `services/gateway/.dockerignore` sí versionado, commit `c39ac7c`.
- No confundir con el repositorio independiente `roboticaLLMIA`.

## Backend US-012/013/014
- Suite Python backend con Firestore Emulator: **84 passed, 1 skipped, 8 warnings** (evidencia previa, no reejecutada en este corte).
- Artifact Registry digest inmutable: `sha256:fb46e00c5c5469fce1138efdda4634b2a1316668d8cf27c9a96c6c51b3a9955e`.
- Cloud Run `smartroute-api-staging` revisión `00013-yev`, tag `us014-backend-test`, URL:
  `https://us014-backend-test---smartroute-api-staging-mkqutd4koq-uc.a.run.app`.
- Revisión Ready/ContainerHealthy; **0 % tráfico principal**. Tráfico API principal previo permanece en `00010-juz` (100 %), según última comprobación.
- Smoke directo: `GET /health` HTTP 200; OpenAPI publica GET ruta propia y POST start/deliver/fail/complete; POST anónimo HTTP 403 (Cloud Run IAM). **No se ejecutaron operaciones de escritura**.

## Gateway US-014
- Suite gateway en Cloud Shell: **24 passed, 1 warning in 1.09s**. Total pruebas de suites backend + gateway: **108 passed** (aparte de 1 skipped backend). Tests del gateway usan mocks: no constituyen prueba E2E.
- `services/gateway/app/main.py` admite los endpoints DRIVER US-012/013/014; limita destinos backend a una allowlist; obtiene token IAM con audiencia de URL canónica y reenvía token Firebase distinto.
- Imagen `smartroute-gateway:us014-c39ac7c`, digest `sha256:552f2e41fe9fe266ebd6d33eb89f37d520f91fad19734b017bada81bd69fca15`. Cloud Build STATUS SUCCESS, 46 s.
- Cloud Run `smartroute-gateway-staging` revisión `00014-gux` con tag `us014-gateway-test` y URL:
  `https://us014-gateway-test---smartroute-gateway-staging-mkqutd4koq-uc.a.run.app`.
- Configuración revision `SMARTROUTE_BACKEND_URL` apunta al backend etiquetado US-014, `APP_ENV=staging`, gateway habilitado.
- Revisión Ready/ContainerHealthy, **0 % tráfico principal**; gateway previo `00011-quj` mantiene **100 %**, según última comprobación.
- Smoke gateway en URL etiquetada: `GET /health` HTTP 200, `GET /api/v1/driver/me/route` sin Firebase HTTP 401, `POST /api/v1/driver/me/route/start` sin Firebase HTTP 401. **No existe aún prueba positiva autenticada gateway → API privada → Firestore**.

## Android — compilación antes del corte
- `apps/driver-android/app/src/main/java/pe/edu/upn/smartroute/driver/di/AppContainer.kt` publicado commit `5b3f7fe`.
- `GATEWAY_BASE_URL = "https://us014-gateway-test---smartroute-gateway-staging-mkqutd4koq-uc.a.run.app"`
- `FORCE_DEMO = false`
- `ENABLE_DELIVERY_MUTATIONS = false` (**no activar** hasta prueba E2E deliberada).
- Autenticación real: `FirebaseAuthRepository.kt`, Google Sign-In; requiere configuración Firebase local válida; modo demo si no se dispone de Firebase.
- Windows PowerShell en `D:\Desarrollo\SmartRoute_AI_US012\apps\driver-android`: `.\gradlew.bat :app:testDebugUnitTest :app:assembleDebug` → **BUILD SUCCESSFUL in 2m 30s**, 42 actionable tasks (8 executed, 34 up-to-date). No instalación en emulador realizada tras este build.

## Restricciones / no tocar
- Base Firestore aprobada `smartroute` en GCP `proyectopersonal-480420`, región Cloud Run `us-central1`. No usar `(default)` ni `gestioncitas`.
- QA DRIVER UID `zMuwbYHLfST2QNdNkfosoCbUZ003`, ruta `21e3de4b-4002-5870-bc4e-8eafb2826219`; último estado conocido PLANNED, versión 2, no revalidado en esta pausa.
- Manuel DRIVER UID `vOQhaUvQW2TZ0m03crKUTwhqhGJ3`, ruta `681f7f60-3a77-5f6b-975e-578fb03e4204`. **Nunca ejecutar mutaciones sobre ruta de Manuel**.
- No asignar tráfico principal a revisiones US-014; no efectuar merge del PR #56.
- No copiar ni registrar Firebase ID tokens, Google ID tokens, secretos ni `google-services.json` en GitHub/chat.
- El modo DEMO y las pruebas JVM no demuestran acceso real a Firestore. Endpoint privado puede denegar invocación si IAM falla: diagnosticar antes de cambiar seguridad.

## Paso exacto para reanudar
**Paso 325 — iniciar el emulador en Android Studio, verificar detección ADB, sin interacción de negocio:**
1. Abrir Android Studio con `D:\Desarrollo\SmartRoute_AI_US012\apps\driver-android`.
2. Tools → Device Manager → iniciar emulador.
3. PowerShell:
   ```powershell
   $ADB = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
   & $ADB devices -l
   ```
4. Esperar salida `emulator-#### device`, número variable; si está vacío, diagnosticar el emulador.
5. Solo después: instalar APK, iniciar sesión con **cuenta QA** y verificar `GET /api/v1/driver/me/route` de solo lectura. Confirmar identidad QA y versión/ruta antes de cualquier POST.
6. Si la cuenta no dispone de Firebase configurado o Google Sign-In no funciona en el AVD, detener y diagnosticar. No habilitar `ENABLE_DELIVERY_MUTATIONS`.

**Corte solicitado por el usuario antes de iniciar paso 325.**