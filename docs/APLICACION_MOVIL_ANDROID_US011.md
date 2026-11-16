# Aplicación móvil — Integración Android con US-011

**Proyecto:** SmartRoute AI, UPN Capstone. **Módulo:** `apps/driver-android/`. **Origen:** revisión del proyecto Android Studio `smartroute-driver-android_20261115_v2.zip`.

## Matriz de integración

| Flujo | Sistema / contrato | Comportamiento |
| --- | --- | --- |
| Acceso | Firebase Authentication con Google | El SDK obtiene un Firebase ID token; el servidor verifica `DRIVER` |
| Ruta propia | `GET /api/v1/driver/me/route` | Consulta HTTPS al gateway, nunca a Firestore ni API privada |
| 200 | `DriverRoute` | Mostrar depósito, paradas ordenadas, kilómetros y minutos estimados |
| 204 | Sin ruta | Mostrar estado sin asignación |
| 401 | Token inválido | Refrescar una vez y reintentar |
| 403 | Rol incorrecto | Rechazar acceso; no elevar permisos |
| 409 | Reserva inconsistente | Mostrar conflicto, sin alterar datos |
| 5xx / desconexión | Servicio no disponible | Mensaje y reintento |

## Revisión estática del proyecto adjunto

- Existe implementación nativa **Kotlin + Jetpack Compose**, Firebase Auth, Credential Manager, osmdroid, módulos `domain/data/di/ui`, Mock y adaptador HTTP del gateway.
- El parser del proyecto recibido coincide con `services/api/app/driver_assignment.py` (campos `id/status/depot/stops/optimized_seconds/optimized_meters/data_origin/assigned_at`).
- Mejoras preparadas en el ZIP revisado: invalidar caché por UID/salida de sesión y rechazar secuencias de paradas no consecutivas, con pruebas nuevas.
- `PLANNED` y `RESERVED` se verificaron en Firestore para una ruta de seis paradas. **No se ha ejecutado una APK Android ni un build Gradle en esta revisión.**

## Seguridad y restricciones

Configurar Firebase Android con paquete `pe.edu.upn.smartroute.driver`, SHA-1/SHA-256 de firma y `app/google-services.json` local **sin versionar**. Solo se permite el gateway `https://smartroute-gateway-staging-913797829604.us-central1.run.app`. La ruta del DRIVER se determina en el servidor por el UID del token Firebase; no se envía el UID del usuario como parámetro de consulta. No hay endpoints implementados para cambiar estado, GPS de ruta activa o completar entregas.

## Evidencia pendiente de ejecutar

1. Importar la carpeta completa del ZIP revisado a `apps/driver-android/` en esta rama.
2. Ejecutar `./gradlew testDebugUnitTest` y `./gradlew assembleDebug` en Android Studio y adjuntar los logs.
3. Probar inicio de sesión de Manuel y respuesta 200 con seis paradas, además de casos 403/204/sin conexión.
4. Integrar el PR solo después de revisión de seguridad, CI y prueba Android.

**Nota de trazabilidad:** hasta importar el ZIP, esta rama contiene documentación de integración, no la totalidad del código Android.