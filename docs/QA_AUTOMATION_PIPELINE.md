# SmartRoute AI — QA Automation Pipeline

## Entrega

Workflow: [`.github/workflows/qa-automation.yml`](../.github/workflows/qa-automation.yml). Se activa en `pull_request`, `push` a `feat/mobile-driver-android-base` y `workflow_dispatch`.

**Objetivo:** detectar regresiones antes del merge del PR #56. Los jobs no usan credenciales GCP ni escriben en bases reales.

## Dos ámbitos separados de pruebas

### 1. CI automático — emuladores (implementado)
- Backend: Python 3.12, pytest, Firestore Emulator, Java 25. Suite completa, incluidas pruebas transaccionales e idempotencia. Artifact JUnit: `qa-backend-firestore-junit`.
- Gateway: pytest, mocks de autenticación/forwarding. Artifact: `qa-gateway-junit`.
- Android: Java 21, Gradle, `testDebugUnitTest` y `assembleDebug`. Artifact JUnit: `qa-android-junit`. La APK QA no se publica como artifact.
- Operador web: instalación de dependencias y build Vite/Docker (no hay tests Playwright todavía).
- `qa-summary`: gate final, falla si alguna tarea no termina en éxito.
- Artifacts retenidos 14 días.

El proyecto de pruebas de Firestore es siempre `demo-smartroute`. El script `scripts/qa/run-api-emulator-tests.sh` exige `FIRESTORE_EMULATOR_HOST` local y detiene la ejecución si falta. No se usan secretos, WIF, Google Cloud Run ni el proyecto compartido.

### 2. E2E controlado — revisiones aisladas Cloud Run (existentes; NO automatizadas aquí)

**No confundir una rama de código Git con la revisión Cloud Run etiquetada y sin tráfico principal.** El código de QA está en la rama Git `feat/mobile-driver-android-base`, PR #56 abierto y sin merge. Los endpoints E2E de Cloud Run existentes son:

- Gateway: servicio `smartroute-gateway-staging`, revisión `00014-gux`, etiqueta **`us014-gateway-test`**, URL `https://us014-gateway-test---smartroute-gateway-staging-mkqutd4koq-uc.a.run.app`.
- API: servicio `smartroute-api-staging`, revisión `00014-xux`, etiqueta **`us014-backend-test`**, URL `https://us014-backend-test---smartroute-api-staging-mkqutd4koq-uc.a.run.app`.
- Ambas revisiones etiquetadas reciben **0 % del tráfico principal**. Son accesibles por URL de etiqueta, por tanto 0 % **no significa inaccesibles**.
- Tráfico principal conservado al cierre QA: gateway `00011-quj` 100 %, backend `00010-juz` 100 %.
- Datos E2E: Firestore nombrado `smartroute` (proyecto GCP `proyectopersonal-480420`). La guardia QA backend restringe mutaciones al conductor y ruta de prueba. Nunca escribir en `(default)` o `gestioncitas`.
- **Prohibido en este pipeline:** `gcloud run deploy`, `gcloud run services update-traffic`, retag automático, merge PR, cambios IAM o ejecución de POST contra Firestore real.
- El último recorrido QA terminó `COMPLETED` versión 10; cinco órdenes `DELIVERED`, una `FAILED`, reserva liberada. **No reutilizar la ruta cerrada** para otro ciclo E2E; preparar datos sintéticos nuevos y autorizar la prueba por separado. Ruta de Manuel fuera de alcance.
- Cualquier futura automatización E2E sobre Cloud Run requiere **workflow separado y manual**, confirmación explícita del alcance, rutas de prueba nuevas, política QA autorizada, verificación de integridad previa/posterior y aseguramiento del **0 % de tráfico principal**. Nunca atarlo a cada `push`.

## Cómo usar

1. En GitHub, abrir **Actions → SmartRoute QA Automation**.
2. Ejecutar **Run workflow** sobre `feat/mobile-driver-android-base` o actualizar PR #56.
3. Revisar el gate **QA gate summary** y los artifacts JUnit de los jobs.
4. Ante una falla, inspeccionar el job y corregirlo antes de considerar merge. No modificar tráfico Cloud Run.

## Límites actuales

- Operador web: build automatizado; **no** hay suite de navegador Playwright implementada.
- Android: test JVM/build automatizados; **no** hay ejecución de pruebas instrumentadas sobre Android Emulator en CI.
- No existe aún E2E automático entre operador, backend y Android con Firebase Auth Emulator.
- La reducción del 20 % en tiempo de entrega sigue siendo hipótesis; requiere evaluación comparable con datos reales u observados.
- Las evidencias `docs/evidence/US012_US013_US014_QA_FINAL_PASS_2026-11-21.md` corresponden a una ejecución real controlada, no a este pipeline automático.

## Ejecución y validación

La publicación del workflow en GitHub **no implica que Actions haya terminado en verde**. Confirmar el resultado del primer run en PR #56 / Actions y resolver dependencias de runner si aparecen; en particular, Java 25 para la versión actual del Firestore Emulator.
