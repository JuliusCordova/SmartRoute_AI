# US-016 — Centro de Distribución configurable por dirección (22/11/2026)

## Decisión
En el operador React se cambia el concepto visible **Depósito / Almacén** por **Centro de distribución**. Se configura con nombre libre, búsqueda de dirección con la API ya existente de Geoapify, selección de sugerencia y confirmación explícita si la geocodificación es aproximada. La UI muestra las coordenadas resueltas, no obliga a introducir latitud/longitud manualmente.

## Contratos y alcance implementado
- Reutiliza **GET /api/v1/geocoding/autocomplete?q=...** con token Firebase, Geoapify y restricciones geográficas del piloto Lima en el Backend. No expone la API key.
- El centro seleccionado sustituye el `depot` de **POST /api/v1/optimization/preview** y **POST /api/v1/optimized-routes**. Se mantiene el nombre técnico `depot` del contrato para compatibilidad sin migraciones.
- El nuevo centro es origen y retorno de **rutas nuevas**. Una ruta guardada conserva sus propias coordenadas: seleccionar otra ruta no modifica documentos ni optimizaciones persistidas.
- La ubicación inicial histórica (-12.095, -77.035) se mantiene como **preconfiguración explícitamente sin verificar** para no romper el MVP. El usuario puede reemplazarla por dirección geocodificada.
- Nombre y selección viven en el estado de la sesión del operador; **el nombre del centro aún NO se guarda como entidad maestra** en Firestore, porque el contrato actual de rutas sólo almacena coordenadas. No se debe afirmar administración persistente de múltiples centros.
- Para aproximaciones se exige marcar confirmación; ante edición de la búsqueda se invalida la selección anterior y no se puede optimizar ni guardar hasta volver a seleccionar.
- Conserva bloqueo de 1 vehículo/10 paradas, chequeo del área piloto, OSM/Leaflet, ORS, OR-Tools y autenticación existente.

## Criterios de aceptación
| ID | Escenario | Resultado requerido | Estado |
| --- | --- | --- | --- |
| AC-CD-01 | Buscar dirección del centro autenticado | Mostrar hasta 5 sugerencias del backend y seleccionar una | Código implementado; QA UI pendiente |
| AC-CD-02 | Ubicación exacta | Aceptar coordenadas en área piloto y habilitar optimizar | Código + prueba lógica; E2E pendiente |
| AC-CD-03 | Ubicación aproximada | No habilitar optimización hasta confirmar | Código + prueba lógica; E2E pendiente |
| AC-CD-04 | Editar dirección seleccionada | Invalidar selección, preview e idempotency key anteriores | Código implementado; E2E pendiente |
| AC-CD-05 | Optimizar y guardar | Payload de depot con coordenadas del centro confirmado | Código + prueba lógica; E2E pendiente |
| AC-CD-06 | Elegir nueva ubicación | Rutas ya persistidas mantienen su depot original | Contrato sin cambios; regresión E2E pendiente |
| AC-CD-07 | Búsqueda fuera del piloto | Rechazar punto y no inventar coordenadas | Prueba lógica añadida; E2E pendiente |

## Evidencia requerida
Capturas de búsqueda, sugerencias, selección, confirmación de precisión aproximada, mapa del origen elegido, comparación y ruta guardada con las coordenadas correctas. Sin capturas E2E no se declara US aceptada. Añadir luego a matriz académica y al anexo del informe.

## Arquitectura / seguridad
Flujo: React (token Firebase) → Gateway autorizado → FastAPI privado con Geoapify desde Secret Manager → dirección/coordenadas → React → endpoint de optimización con coordenadas seleccionadas → Firestore `smartroute` únicamente al guardar ruta. No se toca `(default)` ni `gestioncitas` ni se cambia IAM/tráfico Cloud Run por este PR.

## Pendiente evolutivo
Si la operación requiere múltiples centros guardados entre sesiones, crear una historia específica de catálogo maestro `distribution_centers` con API CRUD, autorización OPERATOR y referencia `distribution_center_id` en rutas; no implementado en este incremento.
