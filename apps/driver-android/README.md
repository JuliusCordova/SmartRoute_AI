# SmartRoute AI — Aplicación móvil del conductor (Kotlin + Jetpack Compose)

La app del repartidor tiene dos modos. Los elige sola al arrancar:

| Modo | Cuándo | Datos |
|---|---|---|
| **Backend real** | Existe `app/google-services.json` | Ruta asignada por el operador, leída de `GET /api/v1/driver/me/route` a través del gateway, con el token de Firebase. Dato **estimado** (matriz vial). |
| **Demostración** | Sin `google-services.json`, o `AppConfig.FORCE_DEMO = true` | Ruta ficticia de 5 paradas en Lima. Dato **sintético** y aviso permanente en pantalla. |

## Contrato que consume (en `main`, PR #55)

`GET /api/v1/driver/me/route`: solo el rol `DRIVER`. El servidor identifica al repartidor por su token; la app no envía su UID.

| Respuesta | Qué hace la app |
|---|---|
| 200 `DriverRoute` | Muestra la ruta: depósito, paradas en orden, km y min estimados |
| 204 | «No tienes rutas asignadas por ahora» |
| 401 | Renueva el token una vez y reintenta; si sigue en 401: «Tu sesión venció» |
| 403 | «Tu cuenta no está habilitada como repartidor» (falta `users/{uid}` con `role=DRIVER`, `active=true`) |
| 409 | «Tu ruta asignada tiene un problema en el servidor» |
| 5xx / sin red | Mensaje de servicio no disponible o sin conexión, con «Reintentar» |

El contrato **no trae el estado por parada, ni la ventana horaria, ni el nombre del depósito**. Por eso las paradas se muestran como «Por entregar» y esos campos se ocultan. El parser rechaza todo lo que se salga del contrato: estado distinto de `PLANNED`/`ACTIVE`, `data_origin` distinto de `estimated`, de 0 a más de 10 paradas, secuencias o pedidos repetidos, coordenadas fuera de rango.

## Pantallas

- Bienvenida: «Ingresar con Google» (backend) o «Ingresar en modo demostración».
- Mis rutas: la ruta asignada con su avance; botón para actualizar.
- Detalle de ruta: mapa OpenStreetMap (depósito «D», paradas numeradas, atribución), métricas y lista ordenada.
- Detalle de pedido: dirección, pedido, coordenadas y estado. Las acciones de entrega están **deshabilitadas** porque el backend aún no tiene el endpoint de transiciones.

## Arquitectura (hexagonal pragmática)

```
app/src/main/java/pe/edu/upn/smartroute/driver/
├── domain/        Modelos (BR-02, BR-03, BR-12), RouteError y puertos RouteRepository / AuthRepository
├── data/
│   ├── remote/    HttpTransport (HttpURLConnection, solo HTTPS), DriverRouteParser, ApiRouteRepository
│   ├── auth/      FirebaseAuthRepository (Google Sign-In)
│   └── mock/      MockRouteRepository, MockAuthRepository
├── di/            AppContainer: elige backend o demostración
└── ui/            auth (Credential Manager), navigation, screens, components, theme
```

## Configurar el modo backend (una vez)

1. **Firebase Console** del proyecto de SmartRoute → *Configuración del proyecto* → *Agregar app* → Android:
   - Nombre del paquete: `pe.edu.upn.smartroute.driver`
   - SHA-1 de depuración: en Android Studio, *Gradle › app › Tasks › android › signingReport* (o `./gradlew signingReport`).
2. Descargar `google-services.json` y copiarlo a `app/`. **No se sube al repositorio** (está en `.gitignore`).
3. El proveedor Google de Authentication ya está habilitado para el panel web; no hay que cambiarlo.
4. Registrar la cuenta de prueba del repartidor según `specs/US-011-DRIVER-ASSIGNMENT.md`:
   - `users/{uid}` con `role: "DRIVER"` y `active: true`;
   - `drivers/{uid}` con `available: true`;
   - en la base nombrada `smartroute`, nunca en `(default)`.
5. *File › Sync Project with Gradle Files* y ejecutar.

## Prueba de punta a punta (staging)

1. En el panel web (operador): crear pedidos, optimizar, **guardar la ruta** y **asignarla** al repartidor de prueba.
2. En la app: *Ingresar con Google* con la cuenta del repartidor → aparece la ruta guardada, en el mismo orden que en el panel.
3. Casos negativos para registrar como evidencia:
   - una cuenta sin rol DRIVER debe mostrar el mensaje de cuenta no habilitada (403);
   - un repartidor sin ruta debe mostrar «No tienes rutas asignadas» (204);
   - en modo avión debe aparecer el mensaje de conexión.

## Ejecutar y probar

```bash
./gradlew testDebugUnitTest          # 27 pruebas JVM: dominio, contrato DriverRoute, repositorio, ViewModels
./gradlew connectedDebugAndroidTest  # 5 pruebas de UI Compose (emulador encendido)
./gradlew assembleDebug
```

Las pruebas del contrato usan un transporte falso: no llaman al gateway ni usan tokens reales.

## Seguridad

- Sin claves, tokens ni `google-services.json` en el repositorio. El token de Firebase lo gestiona su SDK; la app no lo guarda ni lo registra en logs.
- Solo HTTPS, sin redirecciones, con tiempo de espera y respuesta de 256 KB como máximo.
- `allowBackup="false"` y reglas de extracción que excluyen todo (OWASP Mobile M8 y M9). Solo permisos de internet.
- La app llama solo al gateway; nunca a la API privada ni a Firestore.

## Pendiente en el backend para la siguiente etapa

1. Transición de estado del pedido (`IN_TRANSIT`, `DELIVERED`, `FAILED` con motivo) con `Idempotency-Key`.
2. Estado por parada dentro de `DriverRoute` (hoy no viene).
3. Última posición GPS con ruta `ACTIVE` y consentimiento (ADR-10).

## Ubicación en el monorepo

Se propone `apps/driver-android/` junto a `apps/operator-web/`. No subir `.gradle/`, `.kotlin/`, `build/`, `local.properties` ni `google-services.json`.

Si Android Studio avisa que alguna versión de `gradle/libs.versions.toml` no existe o es incompatible (por ejemplo, el plugin `google-services` con AGP 9), acepte la versión que sugiere y vuelva a sincronizar.

## Mejoras de revisión — 2026-11-15

- La caché de ruta está asociada al Firebase UID actual y se invalida al cambiar de conductor; sin sesión no se devuelve una ruta previamente almacenada.
- Se rechazan secuencias de paradas incompletas además de duplicadas.
- Se agregaron pruebas unitarias para aislamiento de caché y secuencia.
- **Estado de evidencia:** revisión estática del código realizada; no se ha ejecutado Gradle ni un emulador Android en este entorno. Los conteos de pruebas documentados son declarativos hasta obtener registros de Android Studio.

## Referencia de backend validada

En el piloto US-011 se confirmó la asignación a un usuario con rol `DRIVER` en Firestore `smartroute`, sin activar la ruta (estado `PLANNED`). La consulta positiva desde esta APK aún requiere una ejecución real en Android Studio con `google-services.json`, Firebase Android SHA y cuenta de prueba.

---

## Bloque integral Android US-012 + US-013 + US-014 (19-11-2026)

**Estado:** implementación de cliente Android y pruebas JVM publicadas en `feat/mobile-driver-android-base`; **no significa que los endpoints US-013/014 existan aún en GCP ni que el APK haya sido recompilado tras este cambio**. Para pruebas finales ejecutar Gradle en Android Studio.

### Funcionalidades Android incluidas

- US-012: confirmación explícita de iniciar ruta y POST `/api/v1/driver/me/route/start`. Se conserva la misma `idempotency_key` al reintentar una operación fallida mientras el ViewModel vive.
- US-013: pantalla de parada con botón **Marcar como entregado**, botón **No se pudo entregar**, confirmaciones, motivo obligatorio (1–250 caracteres), estados y progreso derivados del servidor, rechazo de paradas ya cerradas y POST autenticado.
- US-014: botón **Finalizar recorrido** solo cuando la ruta está `ACTIVE` y todas las entregas figuran `DELIVERED` o `FAILED`; confirmación y verificación de versión.
- Navegación externa hacia la parada por enlace web de Google Maps; sin permisos de ubicación ni seguimiento GPS.
- `refreshRoute()` consulta el estado del servidor y actualiza el detalle al volver de una parada.
- Pruebas JVM: `DeliveryWorkflowTest.kt` para lectura de estados, entrega exitosa/fallida, motivo obligatorio, cierre y rechazos fail-closed.
- **Seguridad:** las operaciones usan exclusivamente gateway HTTPS, Bearer Firebase, versiones y UUID de idempotencia; el cliente nunca escribe directo en Firestore.

### Bandera de seguridad obligatoria

`apps/driver-android/app/src/main/java/pe/edu/upn/smartroute/driver/di/AppContainer.kt`:

```kotlin
const val ENABLE_DELIVERY_MUTATIONS = false
```

Está **desactivada intencionalmente**. Mantener `false` hasta que los tres endpoints nuevos estén implementados y validados en una revisión etiquetada de staging con el conductor QA. El cliente NO simula persistencia ante una respuesta 404, un error HTTP o un recibo inválido.

### Contratos HTTP para backend (propuestos, no confirmados en despliegue)

Todas las operaciones DRIVER requieren `Authorization: Bearer <Firebase ID token>`, JSON, validación de `users/{uid}.role=DRIVER` y `active=true`, y determinación del conductor desde el **token**, nunca desde un UID de cliente.

| Operación | Método y URL | Cuerpo mínimo | Respuesta 200 mínima |
|---|---|---|---|
| Iniciar US-012 | `POST /api/v1/driver/me/route/start` | `{"expected_version":2,"idempotency_key":"<UUID>"}` | `{"id":"<route-id>","status":"ACTIVE","version":3}` |
| Entregar US-013 | `POST /api/v1/driver/me/route/stops/{order_id}/deliver` | `{"expected_version":3,"idempotency_key":"<UUID>"}` | `{"id":"<route-id>","status":"ACTIVE","version":4,"order_id":"<order-id>","order_status":"DELIVERED"}` |
| Fallo US-013 | `POST /api/v1/driver/me/route/stops/{order_id}/fail` | `{"expected_version":4,"idempotency_key":"<UUID>","reason":"Dirección cerrada"}` | `{"id":"<route-id>","status":"ACTIVE","version":5,"order_id":"<order-id>","order_status":"FAILED"}` |
| Cerrar US-014 | `POST /api/v1/driver/me/route/complete` | `{"expected_version":N,"idempotency_key":"<UUID>"}` | `{"id":"<route-id>","status":"COMPLETED","version":N+1}` |

**Requisito imprescindible para el backend:** enriquecer el `GET /api/v1/driver/me/route` con `stops[].status` en `ASSIGNED|IN_TRANSIT|DELIVERED|FAILED` para que el progreso sea autoritativo tras reabrir la aplicación; actualmente el contrato US-011 no proporciona este campo. Mantener el resultado `COMPLETED` consultable hasta que la app pueda mostrar el resumen final (o crear un endpoint de historial/recibo). De otra forma, el cierre de US-014 no es integrable con persistencia y reinicios.

**Contrato de errores esperado:** `401` renovar token una sola vez, `403` rol no autorizado, `404` inexistente/no publicado, `409` conflicto de versión/estado/reserva, `422` payload inválido, `5xx` servicio no disponible. Idempotencia por `(uid, route_id, action, key)`, sin repetir transacciones por retry. Requiere documentación OpenAPI y pruebas en el backend.

**Riesgo de reintentos:** el ViewModel preserva la clave mientras vive. Después de reiniciar el proceso no guarda claves pendientes: antes de repetir una mutación de resultado incierto debe reconsultar el servidor; no prometer entrega offline o exactamente una vez sin mecanismo persistente.

### Caso de prueba real preparado (no ejecutar sobre Manuel)

- Firestore: `proyectopersonal-480420` / base nombrada `smartroute`.
- Conductor QA Firebase + Firestore: `zMuwbYHLfST2QNdNkfosoCbUZ003` (rol `DRIVER`, activo).
- Ruta QA: `21e3de4b-4002-5870-bc4e-8eafb2826219`, `PLANNED`, `version=2`, `driver_id` QA, seis órdenes sintéticas `ASSIGNED`.
- Reserva `driver_assignments/{QA_UID}`: `RESERVED`, `version=1`.
- **Próximo paso 279:** login Android como QA; consultar ruta sin iniciar; validar UID, id, seis paradas y versión; luego ejecutar US-012 solo con aprobación del responsable del piloto.
- Tras publicar US-013/014, validar 6/6 entregas resueltas, progreso y cierre, y comprobar ruta `COMPLETED`, liberación de conductor y eventos auditados en Firestore.
- **No iniciar ni modificar** la ruta Manuel `681f7f60-3a77-5f6b-975e-578fb03e4204`.

### Construcción y pruebas en Windows

```powershell
cd D:\Desarrollo\SmartRoute_AI_US012\apps\driver-android
git pull --ff-only origin feat/mobile-driver-android-base
.\gradlew.bat testDebugUnitTest assembleDebug
# Con el emulador correcto seleccionado:
.\gradlew.bat connectedDebugAndroidTest
```

No versionar `google-services.json` ni pegar tokens en incidencias. El `AppConfig.GATEWAY_BASE_URL` del repositorio está en staging canónico; el emulador de las pruebas anteriores usó una URL etiquetada configurada **solo localmente**. Confirmar el endpoint actual antes de hacer pruebas de mutación.

### Criterios de aceptación para PR #56

1. Android `testDebugUnitTest`, `assembleDebug`, `connectedDebugAndroidTest` satisfactorios **después** de los cambios.
2. Tests de contrato US-012, US-013 y US-014 con backend staging etiquetado y auditoría.
3. Seguridad: driver ajeno 403/404 según diseño, sin mostrar ruta de terceros; no se envían credenciales ni claves en el APK.
4. Un intento repetido con mismo UUID no duplica eventos; versión desactualizada da 409; cierre con una entrega pendiente es 409.
5. Capturas de UI, evidencia de GET/POST sin tokens, cambios Firestore antes/después; pipeline de PR verde.
6. La activación del feature flag y el merge solo luego de que el backend cumpla los contratos; mantener el tráfico principal sin cambios durante pruebas.

La app Android **no** contiene el servicio backend US-013/014, ni sustituye sus transacciones; este bloque desarrolla la contraparte móvil y sus validaciones.

### Demostración Android integral sin backend (US-013/014)

Para validar las pantallas mientras backend publica los endpoints, arrancar **sin** `google-services.json` o con `AppConfig.FORCE_DEMO=true`. La ruta sintética `RUTA-DEMO-001` inicia en `ACTIVE` con 5 paradas, 2 entregadas y 3 pendientes. Es un ejemplo aislado de la ruta QA real. Procedimiento:
1. Abrir «Mis rutas» → `RUTA-DEMO-001` y entrar en `PED-1003`, confirmar entrega.
2. Entrar en `PED-1004`, pulsar «No se pudo entregar», introducir el motivo y confirmar.
3. Entrar en `PED-1005`, confirmar entrega.
4. Volver al detalle de ruta: 4 entregadas, 1 fallida, 5/5 resueltas; «Finalizar recorrido» visible.
5. Confirmar finalización; queda `COMPLETED` **solo en memoria del emulador**, sin escribir en GCP. El proceso reiniciado restablece los datos de demostración.

**US-012 no se demuestra con esta ruta sintética, que comienza en ACTIVE**; su flujo real está preparado con el conductor QA, pendiente de validación. La app mantiene el aviso permanente de datos sintéticos. El flag `ENABLE_DELIVERY_MUTATIONS=false` afecta solamente a la modalidad conectada al backend.

## Prueba Android aislada — nueva ruta QA (23/11/2026)

El botón Iniciar recorrido requiere AppConfig.canMutateQaRoute, estado PLANNED y versión de ruta. Ruta de prueba: fb413b71-c963-570f-be61-500e9eadfb7b; conductor QA: zMuwbYHLfST2QNdNkfosoCbUZ003.

- Debug apunta al Gateway QA etiquetado qa-90681ae; release mantiene el endpoint anterior.
- Un build debug habilita el flujo QA **solo para el UID de conductor autorizado**; ya no requiere una propiedad Gradle adicional. El Backend es el límite de seguridad efectivo.
- Compilar localmente con: .\gradlew.bat :app:testDebugUnitTest :app:assembleDebug
- Release mantiene QA_WRITE_TEST_ENABLED=false; ningún usuario obtiene escrituras QA en release.
- El cliente no restringe a un identificador de ruta; **el guard de Backend QA sí conserva el control exacto UID+ruta**. Esto no permite mutar otras rutas desde el servidor.
- En la revisión Backend QA (0 % tráfico principal), comprobar SMARTROUTE_QA_WRITE_GUARD=true, SMARTROUTE_QA_DRIVER_UID exacto, SMARTROUTE_QA_ROUTE_ID exacto, APP_ENV=staging, FIRESTORE_DATABASE_ID=smartroute.
- No tocar la revisión con tráfico normal, otras bases Firestore, tokens ni google-services.json.
- La geolocalización del emulador es simulada, no medición real de recorrido.
