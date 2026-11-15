# Evidencia de prueba funcional — cinco pedidos y optimización vial

**Proyecto:** SmartRoute AI — Capstone UPN  
**Fecha:** 2026-11-15 (hora local America/Lima)  
**Rama de desarrollo:** `feat/operator-web-osm-routing-pilot`  
**PR:** https://github.com/JuliusCordova/SmartRoute_AI/pull/53

## Propósito y alcance de la evidencia

Documentar la prueba manual observada en el panel de operaciones SmartRoute AI, una vez desplegados React/Leaflet, Firebase Authentication, gateway y API privada en Google Cloud Run, Geoapify, Firestore nombrada `smartroute`, openrouteservice y OR-Tools. La evidencia procede de la **captura de pantalla aportada por el operador al equipo durante el piloto**. No sustituye las métricas detalladas del endpoint ni una medición de operación real.

## Ambiente confirmado en pasos anteriores

- Proyecto GCP: `proyectopersonal-480420`; región `us-central1`.
- Web: `smartroute-web-staging`, revisión `smartroute-web-staging-00002-kcr`, URL `https://smartroute-web-staging-913797829604.us-central1.run.app`.
- Gateway: `smartroute-gateway-staging`, revisión `smartroute-gateway-staging-00004-xpr`. Pruebas `OPTIONS /api/v1/geocoding/autocomplete` = **204** con CORS correcto; `GET` sin Firebase Bearer = **401**, antes de prueba autenticada real.
- API privada: `smartroute-api-staging`, revisión `smartroute-api-staging-00005-xs6`, secreto `GEOAPIFY_API_KEY` y `ORS_API_KEY` desde Secret Manager (no escribir claves en el repositorio).
- Firestore: base específica `smartroute`. Perfil del operador registrado activo con rol `OPERATOR`; no almacenar identificadores personales ni tokens en esta evidencia.
- Validación del registro: la aplicación notificó `Pedido creado y consultado desde Firestore.` y mostró pedidos `PENDING` seleccionables.

## Resultado de la prueba de cinco pedidos

**Datos visibles en captura del panel:** cinco pedidos seleccionados; un vehículo; depósito de prueba aproximadamente en `-12.095,-77.035`; mapa OpenStreetMap con trazado vial estimado de openrouteservice. El flujo `Optimizar con OR-Tools` devolvió:

| Métrica | Orden original | Secuencia OR-Tools |
|---|---:|---:|
| Duración presentada (redondeada) | 32 min | 25 min |
| Distancia presentada | 18.55 km | 15.26 km |
| Mejora porcentual mostrada por aplicación | — | **19.43 %** |

La diferencia de distancia sobre las cifras visibles es **3.29 km** (`18.55-15.26`), equivalente a aproximadamente **17.74 %** menos distancia respecto de la ruta original. La diferencia de tiempo sobre minutos **redondeados** es 7 min; calcular `7/32` da **21.875 %**, distinto del **19.43 %** presentado por el motor. La explicación plausible es el uso de duraciones exactas no redondeadas para calcular el porcentaje, pero **se debe verificar directamente en el JSON de respuesta antes de afirmarlo como hecho**. Conservar como cifra de pantalla 19.43 %, sin recalcularla a partir de cifras redondeadas.

El mapa mostró el recorrido, el orden calculado y la leyenda de estimación. Se utilizó la **misma matriz vial estimada** para comparar el orden inicial y el propuesto; el resultado no demuestra una disminución de tiempos observados, consumo real ni garantías de óptimo global. No debe presentarse como KPI operativo definitivo.

## Evidencia técnica complementaria

- GitHub Actions [run 43669053059](https://github.com/JuliusCordova/SmartRoute_AI/actions/runs/43669053059) para el estado anterior del PR: `api-tests` = success, `firestore-emulator` = success, `operator-web-build` = success, `deploy-staging` = skipped. Estos tests **no son una prueba automática de la ejecución real en GCP**.
- Construcción de API mediante Cloud Build: `f652da8f-a069-4ade-a880-5ec02acd94fa`, imagen `smartroute-api@sha256:bdc48ae0576d328c552a8cfe57fe4c838e9f356d4ebaf31335ad8606bb28eae1`; API actualizada en staging.
- Construcción de gateway: `82cf5fde-9a4d-46f4-a765-a4815859ecb1`, imagen `smartroute-gateway@sha256:a1973ecbed5f066c81d072113dd04b15ce6a95482182a20c2f24a98f95a76e31`; gateway actualizado en staging.
- No se adjunta captura binaria a este commit: el equipo debe incorporar al repositorio el archivo fuente de evidencia si precisa una prueba gráfica archivada. La descripción anterior sí refleja los valores proporcionados y visibles en la conversación.

## Alcance completado / pendientes

**Validado manualmente:** login Google con rol OPERATOR, búsqueda geográfica Geoapify, creación/consulta de pedidos en Firestore, selección de pedidos, consulta de matriz vial de ORS, cálculo y visualización de secuencia OR-Tools, mapa OSM, comparación original/optimizada.

**Pendiente:** comprobar duraciones exactas en respuesta JSON, tests E2E automatizados sobre staging, casos de fallos/tiempos límite de proveedor, limitación de cuotas, estimar resultados con distintos órdenes y volumen, persistir ruta optimizada con versión/huella de matriz, asignar conductor, llevar ruta a Android, observar recorrido real. Esta entrega **es previsualización calculada**, no asignación o ejecución del reparto.

## Guía de integración

Esta evidencia pertenece a la implementación *web-first* del PR #53 y se integra junto con el código de API, gateway y frontend. Antes de habilitar despliegue automático a GCP, comprobar variable `GCP_STAGING_ENABLED` y configuración del entorno; el workflow limita `deploy-staging` a `main` con dicha variable igual a `true`. No realizar cambios en servicios ajenos ni en bases `(default)` o `gestioncitas`.
