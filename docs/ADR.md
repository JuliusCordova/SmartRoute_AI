# Architecture Decision Records — SmartRoute AI v2
| ADR | Decisión | Alternativas | Evidencia/razón | Implicación |
|---|---|---|---|---|
| ADR-01 | Flutter Android | Kotlin/PWA | entrega rápida 7 semanas; UX móvil | no iOS MVP |
| ADR-02 | OR-Tools determinista | vecino cercano/exhaustiva | problema combinatorio, calidad y validación | benchmark contra solución exacta en fixtures |
| ADR-03 | Google Routes API | Haversine/OSRM | matriz con red vial, integración maps | cuotas y licencia; mocks CI |
| ADR-04 | Cloud Run con FastAPI | VM/GKE/local | baja carga operativa, escala variable | BD externa, cold starts |
| ADR-05 | Cloud SQL PostgreSQL | Firestore | integridad y auditabilidad, transacciones | gasto fijo y administración |
| ADR-06 | Vertex AI Gemini sin herramientas | no IA/agente autónomo | explica KPI, no autoriza ni calcula | 20 golden tests + fallback |
| ADR-07 | Monolito modular Hexagonal Slice | microservicios monolito plano | dependencia Maps y Vertex testeables sin sobrediseño | ports selectivos, una unidad deploy |
| ADR-08 | Cloud Logging + Budget Alerts | observabilidad externa | trazabilidad y protección económica | configurar quotas/PII redaction |

## Decisión sobre ML propio
No entrenar regresión ETA en siete semanas sin etiquetas reales. Evolución: Vertex AI entrenar/regresar ETA cuando haya datos observados suficientes, medir MAE/p90 vs Maps; model registry y evaluación por versiones. OR-Tools no es un modelo ML y Gemini sí es un LLM (vía Vertex AI). Los seis ADR-01…06 ya se justificaron en informe de campo I; ADR-07/08 son extensión PA-SDD.
## Referencia patrón
[DevPattern — PA-SDD](https://github.com/JuliusCordova/DevPattern/tree/main/patterns/progressive-agentic-sdd) · [Arquitectura Hexagonal Slice](https://github.com/JuliusCordova/DevPattern/tree/main/patterns/architecture) · [MSS](https://github.com/JuliusCordova/DevPattern/blob/main/definition-packs/minimum-sufficient-specification.md). Se adoptan principios, no se copian artefactos de un agente no necesario.
