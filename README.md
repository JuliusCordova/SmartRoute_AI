# SmartRoute AI

**Capstone — Propuesta 7: App móvil de logística de última milla.**

SmartRoute AI es un MVP académico de siete semanas para gestionar pedidos, seguir entregas desde Android y comparar rutas base con rutas optimizadas. **Hipótesis de negocio:** reducir el tiempo promedio de entrega en al menos 20 %, sujeto a validación mediante piloto comparable.

## Fuente de verdad de requisitos

- [Project Charter y Especificación SDD v1.0](docs/SmartRoute_AI_Charter_SDD_v1.md): objetivos, alcance, restricciones, arquitectura, épicas, historias de usuario, contratos API, esquema lógico de datos, aceptación y backlog semanal.

## Decisiones tecnológicas

| Componente | Decisión |
| --- | --- |
| Aplicación móvil | Android con Flutter |
| Dashboard | React |
| Backend | Python / FastAPI en Google Cloud Run |
| Datos | PostgreSQL |
| Mapas y matriz de viaje | Google Maps Platform |
| Optimización de secuencia | Google OR-Tools |
| IA consultiva | Gemini (sin autorización para modificar operaciones) |
| Gestión | Spec-Driven Development, GitHub y Kanban |

## Restricciones del MVP

- Primera validación: un repartidor, un depósito y hasta diez paradas por ruta.
- GPS únicamente durante rutas activas y con permisos adecuados.
- La IA explica recomendaciones pero no ejecuta cambios sobre pedidos ni rutas.
- Métricas reales y simuladas deben identificarse claramente; la mejora del 20 % es objetivo, no resultado confirmado.

## Estado

**Fase de especificación.** Los contratos, esquemas y criterios en el documento son propuestas de implementación, todavía no servicios desplegados.

## Próximos artefactos

`specs/openapi.yaml`, `db/schema.sql`, pruebas de aceptación, estructura inicial de aplicaciones, CI/CD y un Business Case cuantificado.

## Cumplimiento académico UPN Capstone 2026-2

- [Matriz maestra Capstone ↔ SDD](docs/Matriz_Maestra_Capstone_SDD.md): 36 controles basados en T1, EF, plantilla final y mediciones específicas de SmartRoute.
- [Matriz de seguimiento editable (CSV)](docs/Matriz_Capstone_SmartRoute_v1.csv): criterios, evidencias, semanas, prioridad, estado, responsable y resultado observado.

**Regla:** ninguna evidencia se considera validada hasta asociar su comprobante y revisar el criterio. El objetivo de reducción del 20 % permanece como hipótesis a comprobar, no resultado obtenido.


## PA-SDD v2 — arquitectura GCP y documentación ejecutable (diseño)
Este repositorio adopta **PA-SDD MVP** inspirado en [DevPattern](https://github.com/JuliusCordova/DevPattern): especificación suficiente → decisiones arquitectónicas → contratos → implementación → evaluaciones → evidencia. La documentación v2 **no es una implementación desplegada**.

- [SPEC v2 / Minimum Sufficient Specification](specs/SPEC.md)
- [Arquitectura GCP con Gemini Vertex AI y OR-Tools](docs/ARCHITECTURE_GCP.md)
- [Diagrama de componentes GCP Mermaid](docs/diagrams/01-gcp-components.md)
- [Diagrama de secuencia de optimización Mermaid](docs/diagrams/02-route-sequence.md)
- [Máquinas de estados Mermaid](docs/diagrams/03-state-machines.md)
- [ERD Mermaid](docs/diagrams/04-data-erd.md)
- [Flujo de guardrails y evaluación Gemini Mermaid](docs/diagrams/05-llm-evaluation.md)
- [OpenAPI (contrato propuesto)](specs/openapi.yaml)
- [SQL PostgreSQL (diseño no aplicado)](db/schema.sql)
- [ADRs](docs/ADR.md) · [Seguridad y privacidad](docs/SECURITY_PRIVACY.md)
- [Backlog 7 semanas](specs/BACKLOG_7_WEEKS.md)
- [Criterios Gherkin](tests/acceptance.feature) · [Plan de evaluación](evals/README.md)
- [Trazabilidad académica e ingeniería](docs/SDD_TRACEABILITY.md)
- [Alineamiento informe Práctica de Campo I](docs/CAPSTONE_FIELD_REPORT_ALIGNMENT.md)

**Objetivos académicos ratificados:** OE1 -20 % tiempo por entrega (hipótesis), OE2 reducir km/ruta, OE3 mejorar puntualidad. **El informe preliminar contiene simulación y no demuestra resultados reales.** LLM se despliega conceptualmente vía Vertex AI Gemini como componente read-only; OR-Tools no es ML. Modelo predictivo de ETA en Vertex AI queda fuera del MVP hasta contar con datos observados.
