# SmartRoute AI

**Capstone — Propuesta 7: App móvil de logística de última milla.**

SmartRoute AI es un MVP académico de siete semanas para gestionar pedidos, seguir entregas desde Android y comparar rutas base con rutas optimizadas. **Hipótesis de negocio:** reducir el tiempo promedio de entrega en al menos 20 %, sujeto a validación mediante piloto comparable.

## Estado vigente — 22 de noviembre de 2026 (QA E2E)

**MVP operativo validado en un entorno QA aislado; no es una liberación a producción ni acredita la meta de ahorro del 20 %.** El flujo **Operador web → pedidos sintéticos → OR-Tools + matriz openrouteservice estimada → ruta persistida → asignación DRIVER QA → Android Kotlin/Jetpack Compose → inicio → 5 entregas + 1 incidencia → cierre** se probó con una misma ruta: `aec305db-6e2f-5923-8b9f-87fcd9b37755`. Estado final visible tanto en Android como en el panel del operador: **COMPLETED**, 6/6 paradas resueltas, 5 DELIVERED y 1 FAILED; versión 10 en panel web. La distancia de 16,8 km y duración de 31 min son **estimaciones**, no telemetría real.

- [Acta técnica de prueba integral QA — 22/11/2026](docs/evidence/E2E_OPERADOR_ANDROID_QA_2026-11-22.md): ruta, capturas aportadas en la sesión, endpoints, revisiones Cloud Run y límites de la evidencia.
- [Estado de Capstone y pendientes priorizados](docs/STATUS_CAPSTONE_2026-11-22.md): por componente, demostraciones, deuda de seguridad y próximos gates.
- Código **Android nativo** integrado a `main` mediante PR #60 (commit `44f9748`); la habilitación temporal de escrituras QA para una ruta específica se realizó **solo localmente** en `AppContainer.kt`, y **no** está incorporada en `main`.
- Gateway: commit `5323dee` incorpora la URL de Backend QA v2 a la allowlist. Gateway QA v3 y Backend QA v2 son revisiones **etiquetadas con 0 % de tráfico principal**; las credenciales IAM y la base Firestore `smartroute` se mantienen separadas.

> **Nota de vigencia:** las secciones cronológicas más abajo describen hitos históricos (incluidos Flutter, scaffold y actividades pendientes en ese momento) y no deben utilizarse como estado actual. La decisión vigente de aplicación móvil es **Android Kotlin/Compose**; el panel de mapas usa **OpenStreetMap** y la matriz vial **openrouteservice**, no Google Maps en el flujo verificado.

## Fuente de verdad de requisitos

- [Project Charter y Especificación SDD v1.0](docs/SmartRoute_AI_Charter_SDD_v1.md): objetivos, alcance, restricciones, arquitectura, épicas, historias de usuario, contratos API, esquema lógico de datos, aceptación y backlog semanal.

## Decisiones tecnológicas

| Componente | Decisión |
| --- | --- |
| Aplicación móvil | Android con Flutter |
| Dashboard | React |
| Backend | Python / FastAPI en Google Cloud Run |
| Datos | **Firestore Standard (Native mode)** — pedidos, rutas y estados |
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

**Especificación y bootstrap de FastAPI:** /health y /ready definidos; aún no hay flujo de pedidos, aplicación Android ni servicios GCP desplegados verificados.

## Próximos artefactos

`specs/openapi.yaml`, modelo Firestore, pruebas de aceptación, estructura inicial de aplicaciones, CI/CD y un Business Case cuantificado.

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


## Assisted Agentic SDLC — executable bootstrap

- [Instructions for development agents](AGENTS.md) · [roles/contracts](agents/README.md) · [PROXI Lite policy declaration](policies/proxi-lite.yaml)
- [FastAPI health slice](services/api/app/main.py) · [unit tests](services/api/tests/test_health.py) · [Dockerfile](services/api/Dockerfile)
- [CI workflow](.github/workflows/ci.yml) · [controlled deploy script](scripts/deploy-gcp.sh) · [smoke test script](scripts/smoke-test.sh)
- [SDD release gates](docs/RELEASE_CHECKLIST.md) · [Mermaid assisted-SDLC workflow](docs/diagrams/06-assisted-sdlc.md)

**Status:** source scaffolding, not verified deployment. API health/readiness endpoints only; there is no implemented order CRUD, Firestore integration, Flutter/React or ADK service yet. The build-time assisted agent workflow is not the product runtime architecture. Human approvals and actual CI/IAM must enforce deployments.

## Almacenamiento vigente: Firestore Standard

Para el piloto usamos **Firestore Standard** como única base operativa. [ADR-05-FS](docs/FIRESTORE_STANDARD_MVP.md) · [Colecciones](docs/FIRESTORE_COLLECTIONS.md) · [Diagrama Mermaid](docs/diagrams/07-firestore-standard.md). BigQuery y PostgreSQL son decisiones históricas, no se provisionarán. El objetivo del Capstone es software ejecutable, con pruebas de transacciones y acceso por FastAPI.

## Plan de ejecución del Capstone (7 semanas)

- **[Plan maestro de desarrollo](docs/PLAN_DESARROLLO_7_SEMANAS.md):** vertical slices, dependencias, entregables, roles por asignar, riesgos, costos, gates, validación académica y primera historia a implementar.
- **[Backlog actualizado](specs/BACKLOG_7_WEEKS.md):** calendario relativo S1–S7 y Definition of Ready/Done.

**Prioridad:** producto funcional desplegable con FastAPI + Firestore Standard + Flutter + React + OR-Tools; Gemini consultivo es P1. El estado actual es scaffold de API y especificación; no afirmar ejecución GCP, métricas reales ni funcionalidad P0 completada sin evidencia.

## Inicio de construcción de software — US-003/US-004

Primera vertical versionada: [FastAPI orders API](services/api/README.md), [modelos de pedidos](services/api/app/orders.py), [adaptador Firestore](services/api/app/firestore_repo.py), [autenticación y roles](services/api/app/auth.py), [tests](services/api/tests/test_orders.py). Endpoints `POST/GET /api/v1/orders`. Existen pruebas locales con dobles sintéticos; **pendiente** validación de SDK Firebase/Firestore contra emulador, ejecución de CI y despliegue GCP. Nunca afirmar que los pedidos ya persisten en GCP.

## SDLC Fast Lane (desarrollo asistido con integración continua)

- [Flujo de automatización y configuración de GCP](docs/SDLC_FAST_LANE.md).
- [Instrucciones para GitHub Copilot coding agent](.github/copilot-instructions.md): aplicar SPEC, tests y políticas en cada issue.
- [Ejecución de GitHub Actions](https://github.com/JuliusCordova/SmartRoute_AI/actions): unit, Firestore Emulator, Docker; staging condicional al merge y WIF.
- Siguientes issues: [autenticación y emulator #7](https://github.com/JuliusCordova/SmartRoute_AI/issues/7), [asignación transaccional #8](https://github.com/JuliusCordova/SmartRoute_AI/issues/8), [staging seguro #9](https://github.com/JuliusCordova/SmartRoute_AI/issues/9).

**La automatización de staging requiere configurar variables WIF/IAM, un entorno GitHub staging y permisos GCP mínimos.** No hay despliegue productivo ni backend accesible por Internet generado automáticamente.

## Staging smoke gate (CI)

GitHub Actions valida unit tests, Firestore Emulator y Docker. Tras un merge a `main`, el despliegue privado a Cloud Run **solo se activa si** `GCP_STAGING_ENABLED=true` y se configuran las identidades WIF. La pipeline obtiene un ID token temporal para `GCP_SMOKE_SERVICE_ACCOUNT` y verifica los endpoints `/health` y `/ready`; si fallan, el job falla. **Esto no es todavía una prueba de autenticación de usuario ni persistencia Firestore real.** Ver [SDLC Fast Lane](docs/SDLC_FAST_LANE.md) y [release gates](docs/RELEASE_CHECKLIST.md).

## Optimización de rutas, incremento US-009

Se añade [evaluador OR-Tools](services/api/app/optimization.py) con [pruebas](services/api/tests/test_optimization.py) y [criterios de evidencia](docs/US-009-OPTIMIZATION-SLICE.md). Utiliza una matriz **sintética** de 1–10 paradas, sin invocar Maps ni Gemini ni consumir GCP. El solver es heurístico; no prueba optimalidad global ni ahorro observado. Integración con endpoints, matrices Maps y Firestore queda pendiente.

## Entorno staging autorizado: proyecto GCP existente

Se seleccionó **`proyectopersonal-480420`** para el piloto, sujeto a inventario de solo lectura y aprobación de configuración IAM/costos. Antes de crear Firestore, ejecutar [preflight GCP](scripts/gcp-preflight.sh) en Cloud Shell y revisar el [runbook de configuración compartida](docs/GCP_EXISTING_PROJECT_RUNBOOK.md). El pipeline de staging valida que la identidad y el proyecto coincidan con la elección aprobada. **No significa que Firestore/Cloud Run ya existan ni que se haya consumido GCP.**

### Firestore de SmartRoute (bloqueo de seguridad)

El proyecto GCP compartido contiene datos de Atlas DataGob en Firestore `(default)`; no debe usarse. El backend exige `FIRESTORE_DATABASE_ID=smartroute` fuera del emulador, y GitHub Actions valida el nombre de base en staging. **Esto no crea la base ni implica aprobación de los cargos por lecturas/escrituras/almacenamiento.** Consultar [evidencia](docs/GCP_PREFLIGHT_FINDINGS_2026-11-01.md).

## Firestore creada y gate IAM

El usuario creó y verificó la base **`smartroute` Standard Native** con protección contra eliminación en `proyectopersonal-480420` (2026-11-02 UTC). La infraestructura IAM/WIF y Cloud Run sigue pendiente. Próximo paso seguro: ejecutar [preflight IAM de solo lectura](scripts/gcp-iam-preflight.sh) y revisar [evidencia y diseño de permisos](docs/GCP_FIRESTORE_CREATED_AND_IAM_NEXT.md). No habilitar `GCP_STAGING_ENABLED` sin revisión de privilegios y facturación.

## Incremento propuesto: panel web con OpenStreetMap y optimización vial

- [Operador React y Cloud Run](apps/operator-web/README.md): login Google, pedidos reales vía gateway, mapa OSM, selección de paradas y comparación base/optimizada.
- [Optimización ORS + OR-Tools](services/api/app/route_preview.py): matriz estimada vial desde openrouteservice, retorno con huella y procedencia. **Requiere clave ORS en Secret Manager y despliegue explícito**.
- [ADR-13/ADR-14](docs/ADR-13-14-OPEN-MAPS-WEB-FIRST.md): decisiones cartográficas de bajo costo y desarrollo web-first.

**Estado:** implementación propuesta en PR y pendiente CI/despliegue/GCP E2E. No registrar como rutas persistidas o mejoras observadas. La app Android se construirá después de validar esta demo web.
