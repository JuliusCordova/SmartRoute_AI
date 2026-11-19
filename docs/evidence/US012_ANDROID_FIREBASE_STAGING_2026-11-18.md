# SmartRoute AI — Corte de evidencia Android + Firebase + US-012

**Fecha del corte:** 18–19 de noviembre de 2026 (Perú, UTC-5).  
**Proyecto:** Capstone UPN, SmartRoute AI.  
**GCP:** `proyectopersonal-480420`; región `us-central1`; Firestore base **nombrada** `smartroute` (nunca `(default)`).  
**Repositorio:** https://github.com/JuliusCordova/SmartRoute_AI  
**Rama de trabajo:** `feat/mobile-driver-android-base`, PR https://github.com/JuliusCordova/SmartRoute_AI/pull/56 (**draft**, sin merge a `main`).  
**Alcance:** evidencia de integración móvil US-011, desarrollo US-012, CI local y staging. **No implica aceptación final de US-012.**

## 1. Resumen ejecutivo

- Proyecto Android Kotlin/Jetpack Compose importado desde ZIP revisado a `apps/driver-android/`: **67 archivos, 3289 líneas insertadas**, commit `02c83a9`, publicados en la rama del PR #56.
- Se corrigieron el wrapper Windows `gradlew.bat` (classpath vacío) y compatibilidad de versiones AndroidX con `compileSdk 36.1` (Core KTX 1.17.0, Lifecycle 2.9.4, Activity Compose 1.11.0).
- Android Studio en Windows compiló satisfactoriamente `testDebugUnitTest assembleDebug` (una ejecución con Firebase habilitado: **43 tareas, BUILD SUCCESSFUL**, 1m46s). Nueva versión móvil US-012: **42 tareas, BUILD SUCCESSFUL**, 3m09s. Se volvió a generar APK con **36 tareas, BUILD SUCCESSFUL**, 7s.
- Firebase Android `pe.edu.upn.smartroute.driver` registrado; `google-services.json` colocado **solo localmente** y SHA-1 de debug aceptado. Configuración y secretos no versionados. Android autenticó al conductor piloto mediante Google y consultó efectivamente ruta de seis entregas.
- US-011 **lectura positiva autenticada en Android** corroborada por capturas: vista `Mis rutas`, seis paradas, `PLANNED`, ~15.3 km y 25 min **estimados**; mapa OpenStreetMap cargado en emulador Samsung tras un primer emulador con teselas grises. Las líneas unen puntos, **no** representan trayecto vial calculado.
- US-012: se implementó en la rama móvil el botón `Iniciar recorrido`, confirmación explícita, cliente POST HTTPS, comparación de versión e idempotency UUID. Captura del emulador demuestra **modal de confirmación visible** con opciones `Cancelar` y `Confirmar inicio`. **El POST no se ejecutó**; la transición real no está validada.
- Backend US-012: `GET /api/v1/driver/me/route` se amplió para exponer `version`, tomando el dato de la ruta persistida. Ejecutado en Cloud Shell con entorno `.venv`: **57 passed, 9 skipped, 1 warning** (deprecación de Starlette), tras actualizar dos fixtures para el contrato obligatorio.
- Imágenes API y gateway de prueba construidas con Cloud Build y desplegadas como **revisiones etiquetadas sin tráfico principal**. Disponibilidad y rechazos sin Firebase verificados. Falta prueba funcional autenticada del POST.

## 2. Código y commits relevantes

| Cambio | Referencia |
|---|---|
| Código base Android y tests | `02c83a9` |
| Corrección wrapper Windows | `b6ea1e2` |
| Versiones AndroidX API 36.1 | `ebc866f` |
| Contrato y proyección backend `DriverRoute.version` | commits `ace475f`, `802ea0d` |
| Dominio, parser, puertos Android US-012 | commits `929342e`, `a05ba11`, `e284da7` |
| Transporte HTTP POST + repositorio de inicio | commits `4022a87`, `6b3aa65` |
| ViewModel y confirmación Android | commits `d09392c`, `6728496` |
| Prueba de versión Android | `98f19e3` |
| Fixtures backend actualizadas, 57 tests validados | `eb71be9`, `5b06219` |

Archivos principales:
- `apps/driver-android/app/src/main/java/pe/edu/upn/smartroute/driver/ui/screens/route/RouteDetailScreen.kt`
- `apps/driver-android/app/src/main/java/pe/edu/upn/smartroute/driver/ui/screens/route/RouteDetailViewModel.kt`
- `apps/driver-android/app/src/main/java/pe/edu/upn/smartroute/driver/data/remote/ApiRouteRepository.kt`
- `apps/driver-android/app/src/main/java/pe/edu/upn/smartroute/driver/data/remote/HttpTransport.kt`
- `services/api/app/driver_assignment.py`
- `services/api/app/firestore_driver_assignment.py`
- `services/api/tests/test_driver_assignment_contract.py`
- `services/api/tests/test_driver_own_route_api.py`

## 3. Infraestructura y trazabilidad de despliegues

| Servicio / artefacto | Revisión o imagen | Estado verificado |
|---|---|---|
| API **principal** | `smartroute-api-staging-00010-juz` | **100 %** de tráfico principal, previo al corte |
| API US-012 con versión | `smartroute-api-staging-00012-gac` | **0 %** de tráfico principal; tag `us012-version-test` |
| Gateway **principal** | `smartroute-gateway-staging-00011-quj` | **100 %** de tráfico principal, verificado |
| Gateway integración | `smartroute-gateway-staging-00013-sov` | **0 %** de tráfico principal; tag `us012-version-test` |

**API, Cloud Build** `313a8c24-55f8-46f8-8353-22d52ee786b4`, `SUCCESS`; imagen:
`us-central1-docker.pkg.dev/proyectopersonal-480420/smartroute-staging/smartroute-api@sha256:678b9d4c942a05f15e6925361c686b522a1ec52af17f75aee02fb4ebcf4ea4de`.

**Gateway, Cloud Build** `2b4556a9-776f-4e57-9c8c-82cec5491225`, `SUCCESS`; imagen:
`us-central1-docker.pkg.dev/proyectopersonal-480420/smartroute-staging/smartroute-gateway@sha256:b4f43f250b3628b20e5757fb34400902ab8049de56a952df77bd8f088005b11c`.

- URL de API prueba: `https://us012-version-test---smartroute-api-staging-mkqutd4koq-uc.a.run.app` (Cloud Run **privado**).
- URL de gateway prueba: `https://us012-version-test---smartroute-gateway-staging-mkqutd4koq-uc.a.run.app`.
- API de prueba: `/health` = HTTP **200**, `/ready` = HTTP **200**, `GET /api/v1/driver/me/route` sin Firebase y con IAM separado = **401**.
- Gateway de prueba: `/health` = HTTP **200**, consulta DRIVER sin Firebase = **401**.
- Gateway de prueba utiliza copia temporal de `services/gateway/app/main.py` preparada en Cloud Shell: `PRIVATE_API_URL` apunta a API etiquetada, pero el token IAM mantiene audiencia de la **URL canónica**. Su env `SMARTROUTE_BACKEND_URL` coincide con la URL etiquetada. **Esta variante de gateway es SOLO para pruebas y NO debe promoverse tal cual al tráfico principal.**
- Gateway de prueba corre con `smartroute-gateway@proyectopersonal-480420.iam.gserviceaccount.com`; API con `smartroute-runtime@proyectopersonal-480420.iam.gserviceaccount.com`.
- No hubo despliegue del frontend web en esta fase y no se cambió distribución del tráfico principal.

## 4. Evidencia de Firestore, datos y autenticación

Se hizo lectura de solo consulta con `firestore.Client(project="proyectopersonal-480420", database="smartroute")`:

```text
=== RUTA PILOTO ===
Estado: PLANNED
Versión: 2
Tipo: OPTIMIZED
Cantidad de paradas: 6
VALIDACIÓN DE SOLO LECTURA: OK
```

Ruta piloto: `routes/681f7f60-3a77-5f6b-975e-578fb03e4204`. El valor de versión **2** fue verificado directamente; la pantalla Android mostró lectura autenticada (Manuel), seis paradas y métricas estimadas. **No confundir estimación con desempeño observado**. Ninguna solicitud de inicio `POST /api/v1/driver/me/route/start` fue ejecutada ni validada contra la ruta real.

En la pantalla de detalle de pedido, las opciones `Marcar como entregado` y `No se pudo entregar` permanecen deshabilitadas: **US-013 pendiente**.

## 5. Evidencia visual compartida en las pruebas

Capturas proporcionadas durante la sesión (descripciones basadas en lo mostrado):
1. Android Studio, primer emulador, ruta DEMO: progreso sintético `2/5 = 40 %` y teselas OSM inicialmente grises.
2. Emulador alternativo, ruta DEMO con teselas OpenStreetMap y cinco paradas visibles.
3. Firebase Console registrando app Android `pe.edu.upn.smartroute.driver` e instrucciones SDK.
4. Android autenticado: `Mis rutas` con conductor Manuel, ruta `PLANNED`, 6 paradas, 15.3 km / 25 min estimados.
5. Detalle de ruta en Android, depósito y seis paradas georreferenciadas.
6. Detalle de pedido: acciones US-013 deshabilitadas.
7. Capturas posteriores con el botón de inicio ausente, diagnóstico ADB de dos dispositivos `localhost:63650` y `localhost:63783`; se instaló en el segundo (`SM-S938U`), resultado `Success`.
8. **Captura final de US-012:** pantalla de ruta con diálogo `¿Iniciar este recorrido?`, aviso `PLANNED → ACTIVE`, opciones `Cancelar` y `Confirmar inicio`. **Solo validación visual; no se confirmó inicio**.

**Nota de custodia:** este documento conserva la descripción y trazabilidad de las capturas compartidas en el chat; **los archivos PNG binarios no se incorporan a GitHub en este commit**. Incorporarlos como anexos posteriormente para paquete académico de evidencias, sin publicar información sensible.

## 6. Problemas resueltos y lecciones

- `gradlew.bat`: argumento `-classpath` incorrecto; se corrigió en GitHub.
- Falta de `ANDROID_HOME`: se creó `local.properties` solo en Windows, con SDK local, **no versionado**.
- Incompatibilidad API 36.1 vs versiones recientes AndroidX; se ajustaron dependencias.
- PowerShell antiguo introdujo BOM UTF-8 en `libs.versions.toml`; se reescribió sin BOM localmente.
- Un emulador inicialmente no mostró teselas; el alternativo sí.
- `adb install -r` sin `-s` falló porque dos emuladores estaban conectados. Se seleccionó `localhost:63783`; instalación con `Success`, `force-stop` y `monkey` para ejecutar la APK correcta. Después apareció el diálogo de US-012.
- Cloud Shell con Python global no encontraba `ortools`; con `.venv` `ortools` disponible. Tests backend inicialmente `55 passed, 2 failed, 9 skipped` por fixtures sin `version`; tras corrección **57 passed, 9 skipped**.

## 7. Pendientes obligatorios, sin atribuirles éxito anticipado

1. **US-012:** probar POST de inicio en escenario aislado/sintético con un DRIVER de pruebas diferente de Manuel, y verificar transacción `PLANNED → ACTIVE`, versión+1, reserva `ACTIVE`, evento auditado e idempotencia.
2. Verificar positiva y autenticadamente el campo `version: 2` en `GET /api/v1/driver/me/route` **desde la nueva API/gateway de prueba**; el botón visible indica compatibilidad, pero no se registró cuerpo HTTP explícito.
3. Incorporar pruebas instrumentadas de Android y end-to-end; las **9 pruebas backend omitidas** requieren ejecución/justificación.
4. Asegurar reintentos idempotentes seguros ante pérdida de respuesta: UI actual genera UUID por invocación; una repetición manual sin reutilizar la clave no equivale a retry idempotente. Validar y endurecer este caso antes de activar rutas reales.
5. Promoción controlada de API, con pruebas y plan de reversión; gateway temporal **no promovible sin regresar URL canónica/validar configuración**.
6. Revisar flujo de 401, 403, 409 y pérdida de conectividad, incluyendo conflicto de versión; pruebas móviles/HTTP adicionales.
7. **US-013**: transiciones por entrega, evidencia de entrega/fallo, cierre de ruta y liberación transaccional de reserva; monitoreo web y métricas del piloto.
8. UX: mejorar encuadre/zoom y contraste/accesibilidad del mapa; distinguir línea recta entre paradas de navegación vial.
9. Cerrar PR #56 solo tras revisión; documentar pruebas y evidencias finales académicas.

## 8. Punto de reanudación

**Próximo paso numerado: 264 — inventariar, en lectura solamente, `drivers` y `driver_assignments` de la base `smartroute` para seleccionar un conductor de pruebas libre y preparar una ruta sintética independiente.** No crear/activar la ruta de Manuel ni ejecutar `Confirmar inicio` del piloto. Mantener el PR #56 abierto y el tráfico principal sin cambios hasta aprobación explícita.

**Estimación orientativa de avance funcional comunicada durante la sesión:** ~80 %. **No corresponde a rúbrica final ni reemplaza criterios de aceptación verificados.**

---

## 9. Actualización de ejecución: pasos 264–278 (19 nov 2026)

**Este apartado prevalece sobre el punto de reanudación del §8.** El siguiente paso es **279: autenticación Android con el conductor QA y lectura de su propia ruta**, aún no ejecutado.

### Inspección y creación de identidad QA

- Paso 264, Firestore lectura: `drivers` contenía únicamente al piloto Manuel (`active=true`, `available=true`), pero `driver_assignments` registraba su ruta `681f7f60-3a77-5f6b-975e-578fb03e4204` con `status=RESERVED`, `version=1`. Disponibilidad del perfil **no implica ausencia de reserva**.
- Paso 265, Firebase Auth lectura: tres identidades existentes (Manuel, operador Julio y cuenta alternativa Julius). No se crearon cuentas Firebase.
- Paso 266, Firestore lectura: Julio es `OPERATOR` activo y no tiene perfil `drivers`; la cuenta QA alternativa existía en Firebase pero **no tenía documento** `users`, `drivers` ni `driver_assignments`.
- Paso 267, esquema real en Firestore:
  - `users/{uid}`: `uid` (str), `role` (str), `active` (bool), `created_at` y `updated_at` (timestamps).
  - `drivers/{uid}`: `uid` (str), `display_name` (str), `active`, `available` (bool), timestamps.
- Paso 268, **escritura efectuada en Firestore**: creación de dos documentos para QA UID `zMuwbYHLfST2QNdNkfosoCbUZ003`, `users.role=DRIVER`, `users.active=true`, `drivers.display_name="Conductor QA SmartRoute"`, `drivers.active=true`, `drivers.available=true`. El script utilizó un batch `create` sin sobrescritura; resultado de terminal confirma perfiles creados. No se generó asignación en esta operación.
- La cuenta Julio **conserva OPERATOR** y Manuel **conserva su reserva**. Evitar mezclar roles de pruebas.

### Descubrimiento del flujo y reutilización de ruta sintética existente

- Pasos 269–272: lectura de contrato real `OrderCreate`, `OptimizedRouteCreate`, `AssignDriverRequest` y endpoints. Las paradas **no están embebidas** en `routes/{id}`; se reconstruyen a partir de `order_ids` y `ordered_order_ids`. La ruta optimizada se persiste mediante `POST /api/v1/optimized-routes` y la asignación mediante `POST /api/v1/optimized-routes/{route_id}/assign-driver`, con `expected_version` e `idempotency_key`.
- Paso 273: Cloud Shell estaba en rama `feat/mobile-driver-android-base`, commit local `5b06219` antes de los nuevos commits de documentación. Se detectaron archivos locales no seguidos `apps/operator-web/dist/`, `node_modules/`, `package-lock.json`; **no se limpiaron ni modificaron**.
- Paso 274: se inspeccionó `apps/operator-web/src/main.jsx`; el frontend ya contempla crear órdenes, previsualizar matriz vial y persistir ruta, por lo que se **reutilizó** una ruta previamente creada (sin crear órdenes adicionales).
- Paso 275, Firestore: ruta QA candidata `21e3de4b-4002-5870-bc4e-8eafb2826219` era `status=PLANNED`, `driver_id=null`, `version=1`, `route_type=OPTIMIZED`, `order_count=6`. Ruta de Manuel `681f7f60-3a77-5f6b-975e-578fb03e4204` seguía `PLANNED`, conductor propio, versión 2.
- Paso 276, Firestore: **6/6** órdenes de la ruta QA existen; las seis tienen `status=ASSIGNED`, `data_origin=synthetic`, y `route_id` apuntando exactamente a la ruta QA. Validación automática `True`.
- Paso 277, interfaz del operador: captura confirma `21e3de4b…` marcada **Asignada**, ruta todavía `PLANNED`; estimaciones 56 min / 35.31 km, mejora **estimada** 12.26 % frente a 64 min / 40.43 km originales. Se visualiza conductor QA asociado. **Esta asignación sí se ejecutó** contra Firestore mediante la interfaz (no es solo una propuesta).
- Paso 278, **verificación directa de Firestore tras la asignación**:

```text
RUTA QA: 21e3de4b-4002-5870-bc4e-8eafb2826219
status: PLANNED
version: 2
driver_id: zMuwbYHLfST2QNdNkfosoCbUZ003
order_ids: 6

driver_assignments/{QA_UID}:
route_id: 21e3de4b-4002-5870-bc4e-8eafb2826219
status: RESERVED
version: 1

Asignación consistente: True
```

**Interpretación:** US-011 de asignación QA, desde UI OPERATOR hasta Firestore, comprobado; versiones de ruta y reserva son independientes. El usuario confirmó captura de la UI y salida de Firestore. **US-012 no se ha iniciado todavía** y los seis pedidos QA aún no han entrado en tránsito.

### Estado y punto exacto de reanudación

- **Paso 279, pendiente:** cambiar sesión de Android de Manuel a la cuenta QA, actualizar `Mis rutas` y comprobar que solo aparece `21e3de4b…` (6 entregas, `PLANNED`, 56 min estimados), con botón `Iniciar recorrido`.
- **No pulsar Confirmar inicio** antes de verificar identidad y ruta en Android. Después, para la prueba US-012, ejecutar una sola confirmación sobre **ruta QA**, capturar respuesta y verificar Firestore `ACTIVE`, versión, ocupación y auditoría.
- **Manuel:** no tocar `681f7f60…`, sus seis órdenes ni su reserva.
- Capturas de pantalla de las rutas y asignación QA descritas aquí, **no incorporadas como binarios PNG**.
- Estado del PR: #56 sigue **draft**, sin merge; la rama de trabajo contiene documentación de esta ejecución. No se desplegó software ni se alteró el tráfico de Cloud Run con esta actualización documental.
