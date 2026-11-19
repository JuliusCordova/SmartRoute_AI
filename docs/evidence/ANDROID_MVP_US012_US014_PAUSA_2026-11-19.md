# SmartRoute AI — Checkpoint de pausa Android US-012/013/014

**Fecha:** 2026-11-19 (Perú). **Estado:** PAUSA VOLUNTARIA EN PASO 288.  
**Proyecto:** UPN Capstone SmartRoute AI · **GCP:** `proyectopersonal-480420` · **Firestore:** base nombrada `smartroute`.  
**Rama de código:** `feat/mobile-driver-android-base`. **PR:** [#56](https://github.com/JuliusCordova/SmartRoute_AI/pull/56) (draft, abierto, sin merge).

## 1. Resumen ejecutivo comprobado

El código Android US-012/013/014 está **publicado en GitHub**. El usuario descargó la rama en su laptop Windows y comprobó la compilación y ejecución de pruebas JVM. **No se ha ejecutado la prueba funcional de US-013/014 en emulador**, porque ADB funciona pero no detecta dispositivos activos. **No se han realizado mutaciones de rutas reales durante esta sesión.**

| Elemento | Estado comprobado |
|---|---|
| Directorio local | `D:\Desarrollo\SmartRoute_AI_US012\apps\driver-android` |
| Rama | `feat/mobile-driver-android-base` |
| Commit local tras el último `git pull --ff-only` | `ff0bb69` |
| Resultado del `git pull` | Fast-forward a `ff0bb69` |
| Build y tests | `.\gradlew.bat testDebugUnitTest assembleDebug` → **BUILD SUCCESSFUL in 7s**, 42 tareas, 2 ejecutadas, 40 up-to-date |
| Fallo previo | 1 de 40 tests falló inicialmente al tratar `COMPLETED` como inválido; se corrigió en `DriverRouteContractTest.kt`, commit `ff0bb697` |
| `adb` | No está en PATH, pero `$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe` existe |
| `& $adb devices` | `List of devices attached`, **lista vacía**: ningún emulador conectado |
| Paso actual | **288 — iniciar emulador en Android Studio (Tools → Device Manager)** |

**Importante:** no deducir que se ejecutaron tests instrumentados Compose; el comando que pasó ejecutó tests JVM y ensambló APK, **no** `connectedDebugAndroidTest`.

## 2. Código entregado en la rama

- **US-012:** `POST /api/v1/driver/me/route/start` desde Android, confirmación `PLANNED → ACTIVE`, control de versión, UUID de idempotencia. UI del modal verificada previamente; la **transición real no fue ejecutada**.
- **US-013:** botones de entrega y fallo por parada, motivo obligatorio de fallo, confirmaciones, adaptador HTTP para `POST /api/v1/driver/me/route/stops/{order_id}/deliver` y `.../fail`, pruebas JVM de contratos/errores.
- **US-014:** cierre condicionado a cero paradas pendientes, adaptador HTTP para `POST /api/v1/driver/me/route/complete`, recibo y versión, pruebas JVM.
- Navegación externa hacia las coordenadas de una parada; refresh de ruta y progreso al volver; simulación en memoria **sin GCP** en `MockRouteRepository.kt`.
- **Los endpoints US-013/014 son propuestas de contrato Android**, no están confirmados como implementados/desplegados en el backend. `GET /api/v1/driver/me/route` actual tampoco proporciona estado por parada, requisito para recuperar progreso real tras reinicio.
- La versión Android conectada conserva `AppConfig.ENABLE_DELIVERY_MUTATIONS = false` (fail-closed). **No cambiar a `true` hasta implementar y probar backend**.

Ubicación: [proyecto Android](https://github.com/JuliusCordova/SmartRoute_AI/tree/feat/mobile-driver-android-base/apps/driver-android); documentación: [README Android](https://github.com/JuliusCordova/SmartRoute_AI/blob/feat/mobile-driver-android-base/apps/driver-android/README.md); tests: `app/src/test/java/pe/edu/upn/smartroute/driver/DeliveryWorkflowTest.kt`.

## 3. Estado local que debe protegerse

- Antes de actualizar, `git status --short` mostraba solo `M app/src/main/java/pe/edu/upn/smartroute/driver/di/AppContainer.kt`. Se protegió con:
  ```powershell
  git stash push -m "backup-gateway-us012" -- app/src/main/java/pe/edu/upn/smartroute/driver/di/AppContainer.kt
  ```
- El usuario verificó `stash@{0}: On feat/mobile-driver-android-base: backup-gateway-us012`. **No se ha ejecutado `git stash pop` ni `git stash drop`.**
- El `AppContainer.kt` del repositorio muestra:
  ```kotlin
  const val GATEWAY_BASE_URL = "https://smartroute-gateway-staging-913797829604.us-central1.run.app"
  const val ENABLE_DELIVERY_MUTATIONS = false
  ```
- **La URL del gateway dentro del stash no se llegó a mostrar/comparar**. No restaurar el stash sin comparar y preservar el feature flag nuevo. Puede contener una URL etiquetada de pruebas US-012.
- `google-services.json` es configuración local no versionada. Para ejecutar **modo demo** con la configuración Firebase instalada, usar temporalmente `FORCE_DEMO=true` mediante cambio local controlado y revertirlo después; no tocar Firestore.

## 4. Escenario real QA preparado, pero SIN iniciar

| Variable | Valor comprobado previamente |
|---|---|
| QA Firebase UID | `zMuwbYHLfST2QNdNkfosoCbUZ003` |
| Perfil | `users.role=DRIVER`, activo |
| Ruta QA | `21e3de4b-4002-5870-bc4e-8eafb2826219` |
| Estado/versión | `PLANNED` / `2` |
| Pedidos | 6 sintéticos, `ASSIGNED` |
| Reserva QA | `RESERVED` / versión 1 |
| Prueba pendiente | Login Android QA, lectura propia y luego transición real US-012 controlada |

**Ruta de Manuel protegida:** `681f7f60-3a77-5f6b-975e-578fb03e4204`. No iniciar, cerrar ni modificar.

## 5. Punto exacto para reanudar

**Paso 288:** abrir Android Studio → **Tools → Device Manager** → iniciar emulador existente (no borrar ni recrear dispositivo sin necesidad).

En PowerShell:
```powershell
$adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
& $adb devices
```
Se espera una fila cuyo estado sea `device`; el identificador puede variar.

**Después (no ejecutado):** instalar APK compilada en el emulador correcto; activar modo demo de manera reversible y sin credenciales; ejecutar flujo demo de 5 paradas (2 ya entregadas, 3 pendientes), registrar entrega exitosa, fallo con motivo y cierre; recoger capturas. Probar `connectedDebugAndroidTest`. Finalmente restablecer backend y comparar stash.

**Pendiente aparte:** backend US-013/014, contrato de estados por parada, integración en staging etiquetado, E2E real con conductor QA, observabilidad, seguridad e idempotencia persistente y cierre verificable tras reinicio. PR #56 sigue **draft** y no debe mergearse por el mero resultado `BUILD SUCCESSFUL`.

## 6. Evidencia del usuario

- `git pull --ff-only` local terminó en commit `ff0bb69`.
- `.\gradlew.bat testDebugUnitTest assembleDebug`: `BUILD SUCCESSFUL in 7s`, 42 actionable tasks.
- `Test-Path $adb` devolvió `True`.
- `& $adb devices` devolvió lista vacía. **No se ha confirmado ningún dispositivo Android ejecutándose**.

**No se han subido archivos binarios APK, capturas ni configuraciones privadas al repositorio.**
