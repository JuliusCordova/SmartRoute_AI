# US-010 — Evidencia de recuperación visual de ruta optimizada

**Fecha:** 2026-11-15  
**Ambiente:** staging (GCP `proyectopersonal-480420`, `us-central1`)  
**Rama:** `feat/us010-persist-optimized-routes`  
**Commit de implementación:** `0da032c`  
**Ruta de prueba:** `681f7f60-3a77-5f6b-975e-578fb03e4204`  
**Fuente de evidencia:** capturas de pantalla compartidas por el operador durante la validación manual de la aplicación web.

## Resultado observado

El operador recargó el navegador, abrió **04 · Rutas guardadas** y recuperó la ruta previamente persistida. Confirmó en una nueva captura de pantalla el mapa OpenStreetMap con el recorrido vial estimado en color naranja, las ubicaciones de entrega marcadas y la etiqueta *«Ruta guardada · recorrido vial estimado»*. La tarjeta **05 · Ruta persistida** mostró la misma ruta y conservó las métricas registradas previamente.

| Control | Evidencia observada |
|---|---|
| Recuperación de ruta tras recarga | Correcta |
| Estado persistido | `PLANNED` |
| Número de entregas | 6 |
| Secuencia de entregas y direcciones | Visible en la ruta recuperada |
| Mapa de ruta persistida | Visible con recorrido vial estimado |
| Duración original | 32 min |
| Duración optimizada | 25 min |
| Distancia original | 18.49 km |
| Distancia optimizada | 15.26 km |
| Mejora estimada | 19.47 % |
| Conductor asignado | Ninguno; fuera de alcance de US-010 |

**Precisión:** La ruta vial mostrada es una geometría estimada consultada al recuperar el detalle desde openrouteservice; no constituye un recorrido observado en vehículo. Las métricas son las persistidas por el sistema y no se recalculan al mostrar la ruta. Las rutas previamente guardadas pueden recuperar direcciones de los documentos de pedidos si no contienen snapshots.

## Componentes desplegados al probar

- `smartroute-api-staging`: revisión `smartroute-api-staging-00007-m66`.
- `smartroute-gateway-staging`: revisión `smartroute-gateway-staging-00005-4s5` (sin modificaciones).
- `smartroute-web-staging`: revisión `smartroute-web-staging-00005-n7j`.
- Firestore: base de datos nombrada `smartroute`, sin operar sobre `(default)` ni `gestioncitas`.

## Verificaciones automáticas

GitHub Actions `SmartRoute CI and automated staging`, ejecución #120: `api-tests`, `firestore-emulator` y `operator-web-build` exitosos; `deploy-staging` omitido (el despliegue se ejecutó manualmente).

## Criterio de cierre

La persistencia, recuperación tras recarga y recuperación visual de la ruta fueron observadas en staging. Antes de fusionar la rama debe validarse el estado final del PR y revisar el diff. La asignación de conductor y navegación en Android quedan fuera de US-010.
