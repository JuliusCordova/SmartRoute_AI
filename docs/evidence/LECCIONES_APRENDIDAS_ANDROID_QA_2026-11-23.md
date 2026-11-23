# SmartRoute AI — Lecciones aprendidas y registro de incidentes Android QA

> **Seguimiento posterior del mismo día:** esta sección original documenta un corte **anterior a la resolución** del inicio Android. La [adenda final 23/11](#adenda-post-cierre-qa-23112026) actualiza las incidencias y confirma el cierre E2E 5/5; prevalece sobre los estados de «pendiente» anteriores, sin borrar el historial.

**Fecha del corte:** 2026-11-23 · **Proyecto:** Capstone UPN · **Entorno:** Windows / Android Studio / emulador Pixel 9 Pro XL / Google Cloud Run staging · **Alcance:** pruebas operador → conductor Android → inicio de ruta → GPS.

> Este registro distingue **hechos observados**, **hipótesis**, **correcciones comprobadas** y **pendientes**. No constituye una certificación end-to-end. No se han iniciado recorridos ni enviado posiciones GPS de esta ruta en las evidencias de la conversación. No confundir estimaciones del optimizador con desplazamientos medidos.

## Escenario y baseline

- Repositorio: `JuliusCordova/SmartRoute_AI`.
- Proyecto GCP: `proyectopersonal-480420`; región: `us-central1`; Firestore **nombrada** `smartroute` (nunca `(default)` ni `gestioncitas`).
- Ruta QA planificada y asignada: `fb413b71-c963-570f-be61-500e9eadfb7b`; cinco entregas PENDING, origen SEDE-SUR San Isidro.
- UID conductor QA autorizado: `zMuwbYHLfST2QNdNkfosoCbUZ003`.
- APK Android debug; Gateway QA etiquetado `qa-90681ae`; API QA etiquetada `qa-bca4df3` (la etiqueta se actualizó a revisión `smartroute-api-staging-00017-way`).
- Versión release mantiene el endpoint antiguo y siempre debe permanecer con mutaciones QA deshabilitadas.

## Registro cronológico

| ID | Incidente / evidencia | Causa comprobada o nivel de certeza | Acción / lección aprendida | Estado |
|---|---|---|---|---|
| LL-01 | Disco C: bajo de espacio; AVD de **12.43 GB** en `C:\Users\julio\.android\avd\Pixel_9_Pro_XL.avd`. | Consumo del almacenamiento del emulador. | Copiar con `robocopy` a `D:\Android\avd\Pixel_9_Pro_XL.avd`; verificar 184 archivos, `config.ini` y arranque CLI **antes de borrar** originales. No hay evidencia concluyente en este corte de que se borró el original y se recuperó espacio en C:. | Copia/arranque CLI comprobados; liberación final de C: no verificada |
| LL-02 | Android Studio mostró `Corrupted AVD ini file` tras modificar ruta del AVD. | **Hipótesis plausible:** `Set-Content -Encoding UTF8` en Windows PowerShell generó BOM; no hay prueba aislada que establezca causa única. | Reescribir `Pixel_9_Pro_XL.ini` con `System.Text.UTF8Encoding($false)`. Primeros bytes verificados `61-76-64-2E...` (sin BOM). Emulador volvió a funcionar con Android Studio. | Mitigado |
| LL-03 | `git pull --ff-only` abortó por cambio local en `AppContainer.kt`. | Git protegió cambios locales, rama `main` en commit `5323dee`. | `git stash push` **solo del archivo**, conservar `.venv/`, hacer pull fast-forward y revisar diff sin `stash pop`. Commit actualizado `6f023e4`. | Resuelto; stash conservado |
| LL-04 | El usuario pegó el prompt `PS ...>`, salida `Success` y marcadores `>>` como comandos; PowerShell emitió `AmpersandNotAllowed`, `Get-Process`, comandos no reconocidos. | Copia de transcript completo en lugar de comandos. | Dar **solo comandos limpios**, uno por vez; nunca copiar prefijos de consola ni resultados esperados. | Resuelto |
| LL-05 | Ruta y cinco paradas visibles en Android, pero no aparecía **Iniciar recorrido**. | `RouteDetailScreen` ocultaba el botón si `canMutateRoute` era falso, sin explicar motivo. | Mostrar causa del bloqueo en interfaz **sin quitar el guard**; PR #71 integrado, commit `eee4c82`. La primera pantalla diagnóstica mostró rechazo de autorización QA. | Diagnóstico visible; inicio aún bloqueado |
| LL-06 | `BuildConfig.QA_WRITE_TEST_ENABLED=false` aunque había compilación previa con opt-in. | Valor efectivamente observado en archivo generado; es posible que un build posterior de Android Studio lo regenerara sin flag, **no demostrado**. | `gradlew :app:clean :app:assembleDebug -PsmartrouteQaWrite=true`; comprobar archivo generado con `true`; instalar con `adb install -r` sin pulsar Run (puede recompilar sin flag). | Build `true` e instalación ADB `Success` comprobados |
| LL-07 | `AppContainer.kt` local apuntaba a Gateway `qa-gateway-v3` y ruta antigua `aec305db-...`, mientras `main` incorporó Gateway QA actual y ruta `fb413b71-...`. | Configuración local desactualizada, protegida en stash. | Revisar configuración local vs Git antes de restaurar stash. Mantener la versión nueva con endpoint QA y permisos limitados. | Resuelto en código versionado |
| LL-08 | Revisión API QA `00016-siq` tenía `SMARTROUTE_QA_ROUTE_ID=aec305db-...`, diferente de ruta actual. | Guard del Backend fijado a ruta anterior. | Desplegar **una revisión nueva sin tráfico normal**, conservando `SMARTROUTE_QA_WRITE_GUARD=true`, UID exacto y `FIRESTORE_DATABASE_ID=smartroute`; revisión `00017-way`. Verificación: revisión principal `00010-juz` **100 %**, QA `00017-way` **0 %** con tag. | Resuelto y verificado |
| LL-09 | Confirmación del UID por Firebase Console, ruta `PLANNED`, build QA `true`; sin embargo el botón seguía bloqueado. | UID de la cuenta verificada coincide, pero **no prueba por sí solo** qué `currentUser.uid` mantiene la instancia FirebaseAuth en el proceso Android. `ApiRouteRepository.canMutateRoute` usa `auth.currentDriver.value?.uid`; todavía falta comprobar coincidencia de la sesión Android en ejecución. | No inferir que UID verificado en consola == UID efectivo de la app. Exponer **razones no sensibles** específicas de QA en UI (no tokens, no UID completo). PR #72 abierto. | Pendiente de verificación E2E |
| LL-10 | Se buscó `class DriverRoute` en `main.py` sin resultados; se hicieron múltiples búsquedas de solo lectura. | El modelo está en `driver_assignment.py`, no en `main.py`. | Buscar primero definición en el árbol/repositorio; minimizar comandos manuales. `DriverRoute.version: int = Field(ge=1)`; constructor en `firestore_driver_assignment.py` usa `version=route["version"]`. Esto prueba la **implementación del contrato**, no el JSON recibido por Android. | Modelo localizado; respuesta HTTP real no inspeccionada |
| LL-11 | `adb logcat -d -t 1000 "*:E"` solo mostró `BluetoothPowerStatsCollector`. | Error del servicio Bluetooth del emulador, sin evidencia de relación con SmartRoute. | No interpretar errores globales de Android como fallos de la app; preferir tags/eventos de aplicación y diagnóstico controlado de UI. | Sin acción de producto |
| LL-12 | PR #72 (diagnóstico granular) falló en QA Automation Android al compilar: `Conflicting import: AppConfig is ambiguous`. | **Confirmado por logs de CI:** import duplicado en `RouteDetailScreen.kt`. La primera corrección dejó aún dos líneas de importación; segunda ejecución de QA también falló. | Inspeccionar el archivo real y logs, eliminar todos los duplicados hasta dejar uno. Commit correctivo `24a3390` en rama del PR #72. **No integrar el PR hasta tener QA Android en verde**. | Corregido en rama; pendiente validar nuevo CI |
| LL-13 | PR #72: workflow principal CI verde, pero QA Automation rojo por Android. | Los workflows tienen coberturas distintas. | Requerir **ambos** `SmartRoute CI and automated staging` y `SmartRoute QA Automation` exitosos, especialmente job `Android JVM + debug APK`. | Pendiente de gate final |
| LL-14 | Iteración tuvo demasiados pasos diagnósticos repetitivos y comprobaciones de contrato que no cerraban la causa. | Deficiencia de método de diagnóstico, no evidencia de defecto del Backend. | Priorizar un **árbol de decisión único**: (1) build/flag real, (2) `FirebaseAuth.currentUser.uid` vs guard, (3) `routeId` exacto, (4) `version`, (5) endpoint/respuesta real. La app debe explicar qué condición falla. Mantener un solo paso operativo por interacción. | Mejora de proceso registrada |
| LL-15 | UI muestra `Salida: Depósito` mientras el centro de distribución funcional es `SEDE-SUR San Isidro`. | `DriverRouteParser` usa nombre de depot fijo `"Depósito"`; el contrato presenta coordenadas pero no necesariamente nombre de sede. | Mejorar contrato/UI para preservar el nombre de sede sin cambiar los datos del recorrido. No bloquear QA de inicio por estética. | Deuda de producto |
| LL-16 | Mapa OpenStreetMap une paradas con línea, no con geometría vial; ahorro **14.59 %** es estimación OR-Tools/ORS. | La pantalla advierte que no es trazado por calles; aún no hay GPS real. | Etiquetar claramente `ESTIMATED`; no declarar eficiencia real, tracking GPS ni prueba de campo completadas. | Pendiente evaluación operativa |

## Estado técnico a fecha del corte

**Validado:** sesión funcional de lectura, tarjeta y detalle Android de la ruta, cinco paradas, mapa, estado `PLANNED`, progreso 0/5, estimados 41.7 km/61 min; build debug con flag `true` confirmado una vez y APK instalada por ADB; Backend QA restringido a UID/ruta exactos y 0 % de tráfico principal.

**Bloqueado:** transición `PLANNED → ACTIVE`, visualización efectiva del botón, prueba de consentimiento GPS y entrega de las cinco paradas.

**Pendiente:** PR #72 y CI QA Android; confirmar identidad **en proceso** de Android, distinguir flag/UID/routeId con mensaje concreto, y revalidar versión si supera el guard. **No iniciar rutas automáticamente** como parte del diagnóstico.

## Gates preventivos para reanudar

1. PR #72: QA Automation **Android JVM + debug APK PASS**, y CI principal PASS; hacer merge solo entonces.
2. Windows: sincronizar `main` respetando stash y `.venv/`; compilar `testDebugUnitTest assembleDebug` con `-PsmartrouteQaWrite=true`; comprobar `BuildConfig.QA_WRITE_TEST_ENABLED=true` después del build.
3. Instalar APK mediante `adb install -r` y no pulsar Run en Android Studio. Confirmar texto UI preciso del bloqueo, sin volcar JWT, credenciales ni UID en logs públicos.
4. Autorizar exclusivamente UID+ruta en QA; verificar `APP_ENV=staging`, `FIRESTORE_DATABASE_ID=smartroute`, guard habilitado y **0 % tráfico principal** antes de mutaciones.
5. Solo con confirmación explícita del usuario, ejecutar inicio QA; recopilar evidencia `PLANNED → ACTIVE`; pedir consentimiento GPS específico y advertir que geolocalización del emulador es **simulada**; registrar entregas sin confundirlas con eventos reales.

## Referencias verificables

- PR #70: https://github.com/JuliusCordova/SmartRoute_AI/pull/70 — opt-in debug, gateway/route guard.
- PR #71: https://github.com/JuliusCordova/SmartRoute_AI/pull/71 — mensaje de bloqueo en pantalla.
- PR #72: https://github.com/JuliusCordova/SmartRoute_AI/pull/72 — diagnóstico granular, **pendiente de QA verde/merge al registrar este corte**.
- QA Automation fallido (PR #72): https://github.com/JuliusCordova/SmartRoute_AI/actions/runs/45226880193 y https://github.com/JuliusCordova/SmartRoute_AI/actions/runs/45227459500; ambos evidenciaron importación duplicada.
- Compilación Windows del usuario: `BUILD SUCCESSFUL` con `-PsmartrouteQaWrite=true`, `QA_WRITE_TEST_ENABLED = true`; instalación ADB `Success`.


---

## Adenda post-cierre QA 23/11/2026

**Fuente de evidencia:** [Acta formal SQA E2E cinco paradas](ACTA_CORTE_FORMAL_SQA_E2E_2026-11-23.md). **Resultado:** ruta `fb413b71-c963-570f-be61-500e9eadfb7b` COMPLETED, 4 DELIVERED, 1 FAILED, 0 pendientes; cinco controles de Firestore del cierre **PASS**. La ruta sintética está **congelada**, sin más mutaciones.

### Actualización a lecciones previas

- **LL-05/06/07/09 — BOTÓN INICIAR, guard y compilación:** **resueltos funcionalmente** mediante el [PR #73](https://github.com/JuliusCordova/SmartRoute_AI/pull/73) integrado en `main` (`c309a59`): Android debug autoriza el UID QA sin bandera Gradle adicional, mientras **Backend mantiene el guard UID+ruta**, versión y propiedad. Build normal `assembleDebug` + ADB permitió mostrar «Iniciar recorrido» y completar la ruta. **No** interpretar esto como autorización de escritura de una build release o para cualquier usuario.
- **LL-12/13 — Compilación CI:** PR #72 y PR #73 terminaron con workflows CI + QA Automation exitosos para las correcciones integradas. Deben revisarse las ejecuciones específicas para cifras de tests y comprobaciones negativas.
- **LL-16 — GPS:** pasó de «no validado» a **TESTED QA con emulador**: permiso explícito; posición `-12.097368333333334, -77.02128`, 5 m; Firestore GPS HTTP 200 antes del cierre; eliminación HTTP 404 tras finalizar. **No** equivale a medición física real.
- **LL-14 — Proceso:** los diagnósticos repetidos consumieron tiempo. La simplificación funcional y el motivo explícito de bloqueo resultaron más eficaces. Consolidar verificación en evidencia E2E y limitar comandos manuales.

### Nuevas lecciones posteriores

| ID | Error / hallazgo | Comprobación o causa | Acción preventiva / estado |
| --- | --- | --- | --- |
| LL-17 | Hash SHA-256 de APK generada difiere del binario extraído del emulador en comprobación anterior. | Hash local inicial `93A813...` y extraído `9D378...` no coinciden. La causa exacta **no quedó demostrada** y no debe atribuirse sin prueba a Android Studio ni al método de instalación. | Hacer inspección de identidad/versionName/versionCode de APK en investigaciones futuras; el flujo quedó **resuelto funcionalmente** con PR #73 y compilación normal. |
| LL-18 | Primera transmisión GPS produjo «El servidor no confirmó la operación». | La ventana Location del emulador inicialmente estaba centrada en California, fuera de límites Backend Lima. No se obtuvo código HTTP exacto del primer intento. | Fijar una ubicación simulada de Lima vía Extended Controls → Single points → Set Location. Posterior HTTP 200 en Firestore valida la mitigación; **causalidad original probable, no demostrada**. |
| LL-19 | Confusión entre guardar punto, pestaña Routes y aplicar ubicación del emulador. | «Save route as» y «Saved points» no transmiten necesariamente un GPS al dispositivo. | Guiar captura de posición y botón **Set Location**; un solo paso UI con captura de verificación. |
| LL-20 | La app Google del sistema mostró «Google isn't responding». | Incidencia visible de proceso Google ajeno a SmartRoute; tras «Close app» SmartRoute continuó. | Mantener separadas incidencias de SO/emulador y errores de la app; **no bloqueante**. |
| LL-21 | El reporte GPS se guardó con `data_origin=observed` aunque provenía de emulador. | Campo técnico representa dato de posición recibido; no certifica desplazamiento real. | En informe etiquetar **SIMULATED_QA** y recomendar trazabilidad de origen en diseño futuro; **deuda de gobernanza/datos**. |
| LL-22 | El GPS se elimina cuando se completa una ruta y una lectura posterior devuelve 404. | **Comportamiento intencional:** en backend `complete` elimina `driver_last_locations`; verificado 404. | Leer evidencia de GPS **antes del cierre**, conservar solo prueba mínima saneada y no asumir pérdida de datos o falla. Privacidad conforme al contrato implementado. |
| LL-23 | Resultado «100 %» puede inducir a pensar que el 100 % de pedidos se entregó. | Son **5/5 paradas resueltas**, con **4 entregadas y 1 fallida**. | Reportar separadamente 100 % resolución, 80 % éxito y 20 % fracaso; no reportar entregas físicas reales. |
| LL-24 | Se comprobó directamente en REST el estado de pedidos 1 (DELIVERED) y 2 (FAILED), pero no de los otros tres. | Capturas de Android 3/5,4/5,5/5 y ruta final COMPLETED; faltan tres lecturas individuales independientes. | Transparencia: no atribuir GET REST que no ocurrió; para certificación más estricta se requiere export completo/snapshot auditado. |
| LL-25 | Defecto UI de línea vertical en mapa/detalle y etiqueta genérica «Salida: Depósito». | Visuales de Android; el parser fija nombre de depósito. | Registrar como defectos no bloqueantes con referencia; corregir en un sprint posterior sin alterar retrospectivamente esta ejecución. |
| LL-26 | Las rutas cerradas del 22 y 23/11 son distintas; métricas no comparables como A/B. | Ruta antigua de 6 paradas (5/1), ruta nueva de 5 (4/1), distintas condiciones. | Conservar actas separadas; no afirmar experimento controlado, ahorro real 20 % ni puntualidad observada. |

### Veredicto de seguimiento

**Aprobado** el caso funcional QA de cinco paradas en Android, Gateway, Backend y Firestore; el guard QA permaneció aislado. **Pendiente:** seguridad negativa, export auditado de evidencias, métricas observadas y evaluación de campo. **NO-GO producción** hasta controles adicionales.

Actualización registrada como seguimiento con historial intacto; no confundir la adenda con los estados históricos que figuran en la tabla original.
