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
