# US-V1-008 — Seguimiento GPS original, sin navegación (22/11/2026)

**Estado:** implementado en rama de código; aceptación y despliegue QA pendientes hasta CI + emulador + capturas reales. Se preserva la historia P0 original de `specs/SPEC.md`, RF-07/RNF-03, AC-006/AC-007. No se agrega US-018.

## Alcance entregado

- Android Kotlin: botón visible **Autorizar GPS durante ruta activa** únicamente tras confirmación de inicio y estado `ACTIVE`; solicita permiso `ACCESS_FINE_LOCATION`/ `ACCESS_COARSE_LOCATION` cuando corresponde; el usuario puede detenerlo.
- Mientras la **pantalla de ruta está visible**, obtiene **una posición nueva** de Android LocationManager (GPS o network provider) aproximadamente cada 30 s, con ventana de 12 s; descarta capturas de más de 60 s, sin exactitud o de peor precisión que 500 m. No utiliza posiciones simuladas inventadas ni almacena histórico local.
- Android: POST autenticado solo con Firebase a `/api/v1/driver/me/location`. En demo o sin autorización de mutación QA no se transmite GPS.
- Backend: valida identidad DRIVER, permiso explícito `consent=true`, ruta asignada y reserva `ACTIVE`, ubicación Lima piloto, precisión válida y timestamp con zona horaria reciente. Consulta de Firestore nombrada `smartroute`.
- Solo última ubicación en `driver_last_locations/{route_id}`, origen `observed`; cada envío reemplaza el anterior. La finalización de ruta elimina el documento de ubicación en la misma transacción. No se guarda historial de trayecto.
- Operador: GET `/api/v1/routes/{route_id}/location`, solo rol OPERATOR. La UI ofrece **Consultar GPS** sobre ruta ACTIVE; informa `CURRENT` o `STALE` cuando el último envío supera 120 s y dibuja marcador distinto en el mapa OSM. No confundir con km estimados de ORS.
- El Gateway conserva la allowlist exacta, Firebase, IAM privado y CORS limitado.

## Alcance fuera

Navegación giro a giro/Google Maps, reajuste de OR-Tools, servicio de ubicación en segundo plano, GPS con pantalla apagada, geocercas, historial completo y cálculo de kilómetros observados. El piloto permanece Android foreground-only, con pausa automática al abandonar la pantalla. Esto limita la continuidad de telemetría y debe declararse al sustentar.

## Contratos mínimos

POST `/api/v1/driver/me/location`:

```json
{
  "route_id": "UUID-DE-RUTA-ACTIVE",
  "latitude": -12.095,
  "longitude": -77.035,
  "accuracy_m": 15.0,
  "captured_at": "2026-11-22T15:00:00Z",
  "consent": true
}
```

Respuesta: `{route_id, stored_at, status:"CURRENT"}`. Error **403** si no existe asignación o ruta ACTIVE, identidad ajena, o guard QA rechaza. **422** si datos, precisión, consentimiento o tiempo inválidos. **401** si Firebase inválido.

GET `/api/v1/routes/{id}/location`: `{route_id,driver_id,latitude,longitude,accuracy_m,captured_at,stored_at,status:"CURRENT"|"STALE"}`; **404** si ruta no activa o sin posición. Posición de más de 120 segundos => `STALE`.

## Evidencia y gates de aceptación

| Criterio | Evidencia automatizada | Pendiente manual |
| --- | --- | --- |
| AC-006: rechazar GPS con ruta PLANNED/COMPLETED sin escritura | Firestore Emulator `test_driver_location_emulator.py` | captura de rechazo |
| AC-007: `STALE` a más de 2 min | Python tests + Firestore Emulator | captura en vista operador |
| Identidad autorizada | pruebas de role, uid, route y Gateway | captura de Android autenticado |
| Consentimiento y precisión | Pydantic validation + Android permission gate | captura del permiso Android |
| Detener GPS al cerrar | transacción workflow borra último GPS | captura final tras cerrar |
| Aceptación US-008 P0 | **Pendiente**, no actualizar aún a aceptada | ejecutar ruta sintética nueva; pruebas QA con screenshot/log y SDD |

La ruta QA anterior `aec305db...` ya está COMPLETED, **no se reutiliza** para nuevas mutaciones.

## Privacidad y retención

Solo se guarda el punto más reciente de una ruta activa; al terminar se elimina el documento. La app no solicita `ACCESS_BACKGROUND_LOCATION`, no instala un servicio en segundo plano y no conserva un histórico de posiciones. Si el usuario abandona la pantalla, deja de enviarse GPS y al cabo de 120 s la ubicación se marca STALE. El endpoint de lectura no muestra posición si la ruta ya no está ACTIVE. Si un dispositivo deja de actualizar durante ruta ACTIVE, permanece el último documento hasta cerrar la ruta: antes de usar datos reales fuera de un piloto controlado, definir un procedimiento de eliminación de rutas abandonadas/retención máxima.

**Regla de despliegue:** no tocar Cloud Run/IAM/tráfico, no crear posición real en Firestore durante el PR. Ejecutar CI, emulador y luego una revisión QA etiquetada con 0% tráfico principal y nueva ruta sintética.
