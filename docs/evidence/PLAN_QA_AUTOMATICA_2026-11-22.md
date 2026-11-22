# SmartRoute AI — Ejecución automatizada de regresión — 22/11/2026

**Objetivo:** comprobar sobre el HEAD de `main` (base `c849fa07ccbea5bb9d81f5144fc95fbe39600a59`) los cambios integrados de US-004, dashboard ejecutivo, US-017 y US-008, sin tocar producción ni datos compartidos.

## Plan de validación

| Suite | Workflow | Comprobaciones esperadas | Criterio |
|---|---|---|---|
| Frontend Node | `qa-automation.yml / operator-web` | `npm test --prefix apps/operator-web`: filtros de pedido, búsqueda, KPIs, paginación, centros; `npm run build`; Docker | Tests y build PASS |
| Backend + Firestore Emulator | `qa-automation.yml / backend-firestore` | Suite API y validaciones transaccionales contra proyecto `demo-smartroute`, sin GCP real; GPS consent, stale, y operaciones US-017 | Suite PASS |
| Gateway | `qa-automation.yml / gateway` | Autenticación, proxy allowlist, negación por defecto, GPS/centros | Suite PASS |
| Android JVM + APK | `qa-automation.yml / android` | `testDebugUnitTest` y `assembleDebug` | Tests + ensamblado PASS |
| QA summary | `qa-automation.yml / qa-summary` | Gates anteriores todos en success | PASS |
| CI legado | `ci.yml` | Tests API/gateway, build web y emulador | PASS, staging explícitamente excluido del PR |

## Restricciones y verificaciones manuales posteriores
- No desplegar Cloud Run, no cambiar IAM, ni invocar Firestore `smartroute` de producción/staging.
- La configuración de **QA Automation** usa exclusivamente Firestore Emulator con `GOOGLE_CLOUD_PROJECT=demo-smartroute`, base `(default)` local emulada. Esta base no es la de proyecto personal.
- Tests unitarios prueban cálculos y reglas; **no** sustituyen E2E del navegador con sesión Firebase ni capturas.
- US-004 sólo se acepta en QA de interfaz tras mostrar filtro sobre pedidos existentes, verificar resultados y guardar screenshot.
- Dashboard requiere verificar en UI estados, agregados y etiqueta `estimated`; una prueba de algoritmo no demuestra medición real.
- US-017 requiere confirmar CRUD con cuenta OPERATOR y reversión segura sobre datos sintéticos en una base controlada; no ensayar en datos ajenos.
- US-008 requiere permiso y consentimiento explícitos, captura GPS real y rechazo de usuarios no autorizados; las pruebas del emulador no equivalen a prueba de dispositivo.
- Mantener el 66,7 % de matriz P0 del corte anterior hasta capturas y aceptación actualizadas.
- **Resultados del pipeline:** se incorporan cuando GitHub Actions devuelva conclusiones; nunca declarar PASS anticipado.
