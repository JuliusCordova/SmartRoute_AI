# Arquitectura de componentes SmartRoute AI — Google Cloud (baseline MVP)
**Patrón:** monolito modular + vertical feature slices + puertos/adaptadores selectivos para dependencias externas (Hexagonal Slice de DevPattern). No agente autónomo, no RAG ni Vertex AI Agent Engine para este MVP. Diagrama editable: [Mermaid](diagrams/01-gcp-components.md). 

## Componentes GCP
| Capa | Componente | Responsabilidad | Decisión |
|---|---|---|---|
| Cliente | Flutter Android | sesión, ruta, estado, GPS con consentimiento | objetivo |
| Cliente | React dashboard | pedidos, ruta, métricas, chat de explicación | objetivo |
| Identidad | Identity Platform/Firebase Auth (opcional) o emisor OIDC confiable | tokens para cliente; API valida firma, aud, iss y roles | ADR por implementar |
| Entrada | HTTPS Cloud Run | FastAPI modular con RBAC servidor, validación, rate limits | P0 |
| Datos | **Firestore Standard (Native mode)** | pedidos, rutas, estado, eventos y GPS reciente | P0 |
| Rutas | Routes API (Google Maps Platform) | matriz tiempos real estimada, ruta para mapa | P0 |
| Motor | OR-Tools embebido en Cloud Run | solver determinista de 1 vehículo | P0 |
| IA | Vertex AI Gemini | explica KPI de JSON verificado, sin write tools | P1 |
| Secretos | Secret Manager + IAM service account | secretos y privilegios mínimos | P0 |
| Imagen/entrega | Artifact Registry + Cloud Build o GitHub Actions OIDC/WIF | contenedor y CI/CD sin llaves estáticas | P0 |
| Telemetría | Cloud Logging + Monitoring | logs estructurados, latencias, errores y costo | P0 |
| Seguridad | Cloud Audit Logs y presupuestos | rastreo y control de consumo | P0 |
| ML futuro | Vertex AI entrenamiento/endpoint para ETA | predicción ETA con datos observados, baseline y métricas | FUTURO, no crear coste inicial |

**Ubicación:** preferir región única GCP evaluada por disponibilidad, latencia y residencia de datos; no codificar región como hecho hasta la configuración. **Firestore Standard** opera por uso, sin instancia SQL; controlar lecturas/escrituras, índices y costos. Ver [ADR-05-FS](FIRESTORE_STANDARD_MVP.md).

## Arquitectura interna
`api/routes.py`, `features/orders`, `features/routing`, `features/tracking`, `features/analytics`, `features/ai_explain`, `domain`, `ports` (MatricesPort, ExplanationPort, RepositoriesPort), `adapters` (GoogleRoutes, VertexGemini, Firestore), `security`. Introducir puertos SOLO ante dependencia volátil o test crítico. No microservicios por moda.

## Contratos entre componentes
1. `MapsMatrixPort.get_matrix(depot,stops,departure_time)` devuelve `TravelCostMatrix` validada, fuente, timestamp y versión/huella; bloquear datos incompletos.
2. `RouteOptimizer.optimize(matrix,base_order)` devuelve secuencia válida + costo; no llama LLM.
3. `RouteEvaluationRepository.save(...)` persiste métricas base/optimizadas calculadas sobre LA MISMA matriz (sujeto a licencia).
4. `ExplanationPort.explain(kpis)` recibe sólo agregado minimizado e inmutable; salida JSON schema validado.
5. `OrderEventStore.append(..., idempotency_key)` usa transacción Firestore para evento idempotente + cambio de estado.
6. API responde `X-Correlation-ID` y error uniforme, nunca secretos ni stack traces.

## Seguridad y conectividad
- Service account Cloud Run con invocación a Vertex, secretos autorizados y DB mínima; Cloud SQL mediante conector Cloud SQL / socket seguro y política de egress específica.
- Firestore con servicio Cloud Run e IAM mínimo; sólo FastAPI accede por Admin SDK (server SDK elude reglas). Transacciones para asignación e idempotencia.
- Maps API key restringida a API y entorno; Maps backend con claves privadas protegidas. Firebase/OIDC opcional no elimina autorización de roles en API.
- Telemetría de localización se limita a ruta ACTIVE y consentimiento vigente; al revocar, parar transmisión y depurar según política.
- No afirmar que Google Maps permite cache permanente de matrices; validar términos de servicio, retención y atribución del SDK antes de persistir.

## ¿Dónde entra ML frente a LLM?
**MVP:** OR-Tools (optimización matemática, no ML) + Gemini por Vertex AI (LLM, explicación de solo lectura). **Extensión opcional post-MVP:** Vertex AI Pipelines/Custom Training para regresor ETA usando historial observado (tiempo esperado vs tiempo real; tráfico, hora, zona, distancia), comparar frente a baseline Maps usando MAE y p90 absolute error, sin entrenamiento con datos sintéticos como prueba de desempeño real. No se exige crear un modelo predictivo antes del piloto; solo después de tener datos fiables.

## Costos, riesgos y promoción
El informe contiene estimaciones referenciales que **requieren recalcularse** en las calculadoras oficiales 2026 antes del despliegue, especialmente Firestore/Maps/Vertex. Establecer cuotas, alertas presupuestales y apagado de recursos. G1–G7 documentados en [Backlog](../specs/BACKLOG_7_WEEKS.md). Diagramas de [datos](diagrams/04-data-erd.md), [secuencia](diagrams/02-route-sequence.md), [estados](diagrams/03-state-machines.md) y [flujo de IA](diagrams/05-llm-evaluation.md).

## Revisión vigente

La elección actual es [Firestore Standard](FIRESTORE_STANDARD_MVP.md). [BigQuery ADR anterior](BIGQUERY_PILOT_DECISION.md) es histórico; no desplegar BigQuery ni Cloud SQL en el piloto.
