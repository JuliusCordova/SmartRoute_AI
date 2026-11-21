# Aplicación móvil — Integración Android con US-011

## Alcance

Proyecto Android Studio nativo Kotlin + Jetpack Compose para el rol DRIVER. Fuente: entrega `smartroute-driver-android_20261115_v2.zip`, revisada en esta iteración. Ubicación prevista en el monorepositorio: `apps/driver-android/`.

## Matriz de contrato

| Flujo | Endpoint / sistema | Comportamiento de la app | Verificación |
|---|---|---|---|
| Login Google | Firebase Authentication | Obtiene Firebase ID token mediante SDK; el servidor determina el rol | Prueba real Android pendiente |
| Obtener ruta propia | `GET /api/v1/driver/me/route` | HTTPS al gateway, `Authorization: Bearer` | Cliente y parser implementados; tests de contrato incluidos |
| Ruta asignada | HTTP `200` | Parsear `id`, `status`, `depot`, `stops`, métricas estimadas | Contrato cotejado con `services/api/app/driver_assignment.py` |
| Sin ruta | HTTP `204` | Mostrar estado sin asignación | Prueba unitaria declarada |
| Token expirado | HTTP `401` | Renovar una sola vez | Prueba unitaria declarada |
| Rol no permitido | HTTP `403` | Mostrar error DRIVER | Rechazo observado desde la web OPERATOR con cuenta DRIVER; prueba Android pendiente |
| Reserva inconsistente | HTTP `409` | Mostrar conflicto, no modificar datos | Prueba unitaria declarada |
| Error de red | Timeout / 5xx | Mensaje y reintento | Prueba unitaria declarada |

## Cambios de revisión realizados

- El repositorio de API evita servir ruta almacenada en caché cuando la sesión ya no existe o cambia el UID del conductor.
- El parser rechaza secuencias de paradas no consecutivas, además de IDs duplicados.
- Nuevas pruebas unitarias para aislamiento entre sesiones y secuencias malformadas.

## Evidencia verificada y limitaciones

- **Verificada en backend:** US-011 integrado en `main` (`4867408`), route `681f7f60-3a77-5f6b-975e-578fb03e4204` en `PLANNED`, reserva `RESERVED`, versión 2; evidencia aportada desde Cloud Shell.
- **No verificada en Android:** compilación Gradle, ejecución física, inicio de sesión Android, y consulta 200 desde el teléfono. El archivo ZIP incluye pruebas, pero su ejecución requiere Android Studio/SDK y credenciales de Firebase Android.
- **No implementado:** transiciones de estados, navegación giro a giro, GPS operativo ni entrega completada.

## Seguridad y configuración

- Registrar la aplicación Android (`pe.edu.upn.smartroute.driver`) y SHA de la firma Android en el proyecto Firebase aprobado.
- Descargar `app/google-services.json` desde Firebase. No versionar el archivo, certificados privados, claves o tokens.
- Exigir `users/{uid}.role=DRIVER` y `active=true` del lado servidor. No enviar un UID arbitrario al endpoint de ruta propia.
- Utilizar únicamente `https://smartroute-gateway-staging-913797829604.us-central1.run.app`; nunca llamar directamente a la API privada ni consultar Firestore desde Android.
- La pantalla de mapa muestra conectores esquemáticos entre paradas, no navegación real.

## Pruebas pendientes para cierre de evidencia

1. `./gradlew testDebugUnitTest` con resultado adjunto.
2. `./gradlew assembleDebug` con resultado adjunto.
3. Abrir en Android Studio con `google-services.json` local no versionado y ejecutar con Manuel.
4. Verificar que la ruta asignada aparece con seis paradas, estado `PLANNED`, sin capacidades de modificación.
5. Verificar sin rol DRIVER (403), sin ruta (204) y sin conexión (estado de error).
