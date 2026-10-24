# SmartRoute AI — Minimum Sufficient Specification (MSS) v2.0
**Estado:** baseline de diseño, NO software implementado. **Método:** PA-SDD de [DevPattern](https://github.com/JuliusCordova/DevPattern/tree/main/patterns/progressive-agentic-sdd) en nivel MVP. **Fuente funcional:** Informe Capstone Práctica de Campo I (24-oct-2026) + Charter/SDD v1.0. **Prioridad del informe:** si difieren los objetivos iniciales, prevalecen OE1–OE3 del informe.

## 1. Business intent / pregunta / hipótesis
- Problema: secuencia manual de paradas, ausencia de trazabilidad y de línea base observada en empresa **académica ficticia** de Lima Metropolitana. No atribuir a una empresa real.
- Pregunta: ¿cómo influye SmartRoute AI en la eficiencia de entrega de última milla?
- Objetivo general: mejorar la eficiencia de entrega mediante SmartRoute AI.
- OE1: reducir **≥20 %** tiempo promedio por entrega respecto de línea base.
- OE2: reducir distancia recorrida por ruta con mismas paradas y depósito.
- OE3: incrementar puntualidad frente a línea base.
- Hipótesis: tres mejoras anteriores sujetas a comprobación; **no** garantizadas.
- Meta de software: >=90% requisitos priorizados cubiertos y >=90% necesidades específicas satisfechas, con pruebas.

## 2. Evidencia y advertencia
Simulación preliminar reportada en informe: 30 rutas/233 entregas, 5–10 paradas, tiempo por entrega (min) 23.31 en orden de registro, 16.13 vecino cercano, 15.02 OR-Tools. Diferencia relativa -35.6% vs registro pero solo -6.9% vs vecino cercano. Se usó aproximación geométrica ×1.3, 12.7 km/h y 180 s por parada. **No equivale a datos observados ni prueba que el ruteo real alcance OE1**. Verificar el script y datasets antes de reproducir la afirmación de óptimo exacto frente a Held–Karp.

## 3. Usuarios, necesidades, exclusiones
- Operador: dashboard web para pedidos, asignación, activación y KPI.
- Repartidor: Android para ruta, estado y GPS en servicio autorizado.
- Gerencia académica: evidencia y decisión de continuar el piloto.
- Destinatario: beneficiario indirecto, con direcciones ficticias en demo.
- NEC-01: pedidos y coordenadas estructurados. NEC-02: secuencia con tiempos de viaje. NEC-03: seguimiento estados/GPS. NEC-04: KPI y piloto comparable. NEC-05: explicación IA sin delegación de decisiones.
- IN: depósito único, 1 repartidor, 5–10 paradas, Android, rutas, trazabilidad, dashboard, Gemini consultivo.
- OUT: multi-flota, asignación automática integral, SLA empresarial, ventanas complejas, geocercas comerciales, streaming masivo, chatbot con herramientas de escritura, modelos predictivos entrenados como requisito MVP.

## 4. Historias y prioridad
| Historia | Capacidad | Prioridad | Necesidad | Entrega |
|---|---|---|---|---|
| US-001,002 | autenticación/RBAC | P0 | transversal | S3 |
| US-003,004,005 | pedidos, consulta, asignación | P0 | NEC-01 | S3 |
| US-006,007,008 | ruta Android, eventos, GPS | P0 | NEC-03 | S4 |
| US-009,010 | optimización y publicación | P0 | NEC-02 | S5 |
| US-011 | KPI y dashboard | P0 | NEC-04 | S6 |
| US-012 | Gemini consultivo | P1 | NEC-05 | S6 |
| US-013,014 | incidencia y cola sin conexión | P1 | NEC-03 | S6 |
| US-015 | exportación y datos piloto | P0 | NEC-04 | S7 |

## 5. Requisitos funcionales
RF-01 autenticación RBAC; RF-02 coordenadas validadas; RF-03 consulta pedidos; RF-04 asignación sin duplicidad; RF-05 ruta publicada visible solo al conductor asignado; RF-06 eventos idempotentes; RF-07 GPS únicamente con consentimiento y ruta activa; RF-08 comparación determinista base vs optimizada; RF-09 KPI reproducibles; RF-10 Gemini consultivo P1; RF-11 incidencias/offline P1; RF-12 exportación de piloto con fuentes y limitaciones.

## 6. NFR y reglas
- RNF-01 TLS, JWT/OIDC verificado, RBAC comprobado EN SERVIDOR, secretos gestionados.
- RNF-02 p95 CRUD <1 s sin dependencia externa; solver ≤10 s 10 paradas usando fixtures.
- RNF-03 GPS solo ruta ACTIVE y consentimiento explícito; política de retención documentada antes de piloto.
- RNF-04 idempotencia de cambios estado; cola offline P1 sin falsificar instante observado.
- RNF-05 registrar entrega en <=2 toques desde lista (probar con usuarios).
- RNF-06 OpenAPI versionado, CI y auditoría del despliegue.
- RNF-07 en 20 casos de evaluación LLM, 0 KPI inventados y 0 escrituras.
- BR-01 1 vehículo, depósito, 5–10 paradas. BR-02 estados pedido PENDING→ASSIGNED→IN_TRANSIT→DELIVERED/FAILED (guardas). BR-03 ruta DRAFT→PLANNED→ACTIVE→COMPLETED/CANCELLED.
- BR-04 solo operador crea/optimiza/activa. BR-05 sólo conductor asignado recibe/actualiza. BR-06 un pedido no puede estar activo en dos rutas.
- BR-07 rutas optimizadas deben contener exactamente todas las paradas válidas. BR-08 conservar matrices de evaluación solo en modo y plazo permitido por licencia Maps; si no, guardar huella, origen, hora y fixtures propios, no respuesta Google en bruto.
- BR-09 no afirmar mejora si evaluación <=0; BR-10 Gemini no escribe; BR-11 eventos llevan idempotency key y timestamps UTC servidor.
- BR-12 registrar 'observed' vs 'synthetic' vs 'estimated' en mediciones, jamás agregarlos sin estrato.

## 7. Integraciones / errores
Maps Routes API (computeRouteMatrix/computeRoutes) con quotas, reintentos limitados y validación de elementos; Vertex AI Gemini con salida estructurada, timeout y sin PII; PostgreSQL (Cloud SQL) transaccional; Secret Manager/IAM; Cloud Logging y Monitoring. Si matriz incompleta/inaccesible →422 ROUTE_INFEASIBLE; Maps caído →503 sin inventar ruta; sin permiso →403; datos inválidos →422; asignación conflictiva →409; cuota →429/503 con mensaje y correlación.

## 8. Pruebas y métricas
Ver [tests/acceptance.feature](../tests/acceptance.feature), [evals/README.md](../evals/README.md), [docs/SDD_TRACEABILITY.md](../docs/SDD_TRACEABILITY.md). KPI OE1 = (Tbase - Tpiloto)/Tbase ×100 con tiempos **observados** comparables; OE2 km GPS/ruta; OE3 entregas dentro de ventana/entregas evaluables. Publicar n, origen, ventana, exclusiones y dispersión.

## 9. Quality gate / estado
G1 problema y P0 aprobados; G2 contratos/ADR/UX revisados; G3–G6 tests y demos parciales; G7 informe, piloto etiquetado, resultados y veredicto. Un archivo presente en el repositorio NO significa funcionalidad desplegada. No promover sin evidencia de ejecución.
