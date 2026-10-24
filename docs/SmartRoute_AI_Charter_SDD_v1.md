# SmartRoute AI — Project Charter y Especificación SDD v1.0
**Proyecto:** Capstone — Propuesta 7, App Móvil de Logística de Última Milla  
**Estado:** Baseline propuesta para revisión académica  
**Duración:** 7 semanas  
**Fecha:** 23 de octubre de 2026  
**Modalidad:** MVP académico con operación ficticia en Lima Metropolitana  

> **Trazabilidad:** La propuesta académica original establece app móvil, localización del repartidor, optimización mediante API de mapas, objetivo de reducción de tiempo de entrega del 20 %, Kanban de 7 semanas, Business Case, pre-mortem y criterios de aceptación. Las decisiones arquitectónicas y umbrales restantes de este documento son propuestas de diseño, no exigencias textuales del material original.

# PARTE I — PROJECT CHARTER

## 1. Resumen ejecutivo
SmartRoute AI es un MVP para digitalizar la asignación y ejecución de entregas urbanas, comparar una secuencia de visitas manual con otra calculada por optimización y permitir al operador medir tiempos y distancias. La aplicación Android permitirá al repartidor consultar su itinerario, marcar entregas y compartir su posición durante una ruta activa. Un dashboard web mostrará la operación; un asistente Gemini explicará resultados sin tomar acciones sobre datos operativos.

## 2. Justificación y situación actual
**Contexto supuesto:** empresa ficticia de reparto en Lima, que usa hojas de cálculo, mensajería y navegación individual, sin trazabilidad integral ni optimización sistemática. No se cuenta todavía con estadísticas observadas de su desempeño.
**Problema:** secuencias de entrega definidas manualmente, visibilidad incompleta del estado y falta de métricas confiables para identificar desvíos.
**Oportunidad:** evaluar si la optimización de paradas y la digitalización disminuyen los tiempos y permiten fundamentar decisiones de inversión.

## 3. Objetivos SMART
- **OG:** desarrollar, desplegar y demostrar el MVP al concluir la semana 7.
- **O1:** registrar y asignar pedidos desde un dashboard antes del final de la semana 3.
- **O2:** permitir ejecución de ruta, actualización de pedidos y envío autorizado de GPS en Android antes del final de la semana 4.
- **O3:** generar y comparar una ruta base vs. propuesta para un repartidor y hasta 10 destinos antes del final de la semana 5.
- **O4:** visualizar KPI y explicaciones consultivas de IA antes del final de la semana 6.
- **O5:** medir la reducción del tiempo promedio de entrega en un piloto comparable en semana 7, con **meta de -20 %**; reportar el valor obtenido incluso si no se alcanza.

## 4. Alcance
**Incluye:** autenticación básica de operador/repartidor, pedidos y asignaciones, una ruta diaria por repartidor en el piloto, ubicación GPS con consentimiento durante ruta, integración Routes API, motor OR-Tools para un solo vehículo, comparativa de resultados, dashboard de KPI, asistente Gemini de solo lectura, API y despliegue Cloud Run, pruebas y evidencia.
**Excluye:** app iOS, pagos, ERP, seguimiento permanente, cálculo de fletes, prueba de gran flota, predicción ML entrenada, reasignación automática, ventanas temporales complejas, optimización multivehículo, garantía de tráfico en tiempo real y operaciones autónomas de LLM.
**Configuración piloto:** 1 depósito, 1 repartidor, 5 a 10 paradas por ronda, sin restricciones de capacidad y con tiempos de servicio por parada parametrizados; múltiples recorridos comparables si los recursos permiten.

## 5. Entregables y aceptación global
| Código | Entregable | Evidencia para aceptación |
|---|---|---|
| D01 | Charter, Canvas y Business Case | Aprobación académica; supuestos, VAN/TIR y escenarios documentados |
| D02 | SPEC, arquitectura, modelo y contratos | Historias, esquemas, contrato OpenAPI, diagramas revisados |
| D03 | Backend y persistencia | Endpoints funcionando, autenticación y pruebas |
| D04 | Android | Registro de sesión, ruta, estados, ubicación comprobada |
| D05 | Optimizador | Ruta factible y comparativa reproducible con benchmark |
| D06 | Dashboard e IA | KPI verificables, respuesta de Gemini consultiva y fundamentada |
| D07 | Evidencia piloto y SQA | Dataset, metodología, resultados, defectos y limitaciones |
| D08 | Sustentación | Demo E2E + informe y repositorio versionado |

## 6. Gobernanza del proyecto
**Sponsor:** patrocinador académico / docente (por designar). **Product Owner:** representante de operación simulada (por designar). **Líder técnico:** integrante del equipo (por designar). **Responsable de calidad:** integrante del equipo (por designar). **Usuarios:** operador y repartidor ficticios o participantes de piloto. Roles reales y nombres quedan pendientes de asignación.
- Reunión semanal de seguimiento; revisión de tablero Kanban 2 veces/semana.
- Decisiones de alcance mediante cambio documentado y autorización del responsable del proyecto.
- Cierre de semana con demo, pruebas y decisión go/no-go.

## 7. Hitos y cronograma
S1: contexto, línea base, Canvas, Charter, backlog y SPEC inicial.  
S2: arquitectura, UX, modelo lógico, OpenAPI, configuración de APIs y CI/CD base.  
S3: autenticación, pedidos, asignaciones, base PostgreSQL y pruebas API.  
S4: app Android, rutas asignadas, estados y GPS controlado.  
S5: matriz de tiempos, OR-Tools, comparación base/optimizada y pruebas de integración.  
S6: dashboard, métricas, asistente Gemini y pruebas E2E.  
S7: piloto, calidad, economía, informe y demo final.

## 8. Business Case inicial (sin cifras inventadas)
**CAPEX académico / inversión inicial:** horas de diseño, desarrollo, pruebas, dispositivos y capacitación si se monetizan.  
**OPEX:** servicios Google Maps Platform (especialmente matriz por elementos), Gemini, Cloud Run, base de datos, conectividad y mantenimiento.  
**Beneficios:** combustible ahorrado, horas de repartidor recuperadas, menor reproceso, mayor puntualidad.  
**ROI:** (beneficios netos - inversión) / inversión, con horizonte explícito.  
**VAN:** suma de flujos descontados menos inversión inicial. **TIR:** tasa que hace VAN = 0.  
**Datos pendientes:** volumen diario, kilómetros, costo por hora, consumo combustible, precio por litro, costo de APIs, inversión de horas y tasa de descuento. No presentar VAN/TIR sin estos insumos.

## 9. Matriz de riesgos pre-mortem
| ID | Escenario | Prob. | Impacto | Control / respuesta | Dueño |
|---|---|---|---|---|---|
| R01 | Sin conexión durante reparto | Media | Alto | cache local, cola de eventos, marca temporal, sincronización idempotente | Líder móvil |
| R02 | GPS desactualizado o impreciso | Alta | Medio | edad de ubicación, precisión GPS, no inferir posición en vivo | Líder móvil |
| R03 | Consumo excesivo de Routes API | Media | Alto | límites de tamaño, caché permitido, cuotas y presupuestos | Líder backend |
| R04 | Matriz incompleta / rutas imposibles | Media | Alto | validar celdas, devolver error de factibilidad, sin ruta inventada | Líder optimización |
| R05 | Asistente Gemini alucina KPI | Media | Medio | prompt estructurado, evidencia numérica, respuesta JSON validada | Líder IA |
| R06 | Exposición de ubicación / datos | Media | Alto | RBAC, TLS, consentimiento, retención limitada, secretos gestionados | Líder seguridad |
| R07 | No se logra el 20 % | Alta | Medio | piloto comparable, evidenciar resultado real y límites, no maquillar | Product Owner |
| R08 | Retraso por integración | Media | Alto | mocks desde S2, freeze de funciones P1, pruebas tempranas | Líder proyecto |

## 10. Criterios de cierre y éxito
MVP desplegado y demo funcional, todas historias P0 aceptadas, pruebas críticas en verde, evidencia de control de acceso, comparación reproducible, reporte del piloto con limitaciones, Business Case con supuestos transparentes y material de sustentación. La meta -20 % es un objetivo de negocio sometido a prueba, no una condición para ocultar resultados adversos.

# PARTE II — SPEC-DRIVEN DEVELOPMENT (SDD)

## 11. Fuente de verdad y convenciones
`specs/SPEC.md` es la fuente de verdad funcional. `specs/api/openapi.yaml` define contratos; `specs/data/schema.sql` define DDL; `specs/acceptance/` contiene escenarios Given/When/Then. Cambios en comportamiento requieren PR de especificación antes del código.
Versiones: SPEC v1.0; endpoints `/api/v1`; IDs `EP-xx` épicas, `US-xxx` historias, `AC-xxx` criterios, `TC-xxx` pruebas, `RF-xxx` funcionales. Definición de Done: especificación actualizada, tests automatizados, revisión de código, evidencia de UI y sin hallazgos críticos abiertos.

## 12. Actores y permisos
- **OPERADOR:** crea pedidos, asigna, genera rutas, consulta ubicación vigente y KPI; puede pedir explicación a IA.
- **REPARTIDOR:** consulta exclusivamente sus rutas, marca estado de sus pedidos y reporta ubicación mientras tiene ruta activa y consentimiento vigente.
- **ADMIN (opcional):** configura cuentas y parámetros, no obligatorio en UI piloto; cuentas iniciales por seed seguro.
- **Asistente IA:** no tiene credenciales para mutaciones y solo recibe un payload resumido autorizado, sin PII innecesaria.

## 13. Épicas e historias (backlog priorizado)
| Épica | Historia | Descripción | Prioridad | Semana | Dependencias |
|---|---|---|---|---|---|
| EP01 Fundaciones | US-001 | Como usuario inicio sesión y recibo acceso según rol | P0 | 3 | DB, auth |
| EP01 Fundaciones | US-002 | Como operador veo el panel y navego módulos autorizados | P0 | 3 | US-001 |
| EP02 Pedidos | US-003 | Como operador creo pedidos con destino validado | P0 | 3 | US-001 |
| EP02 Pedidos | US-004 | Como operador consulto y filtro pedidos por estado | P0 | 3 | US-003 |
| EP02 Pedidos | US-005 | Como operador asigno pedidos pendientes a repartidor | P0 | 3 | US-003 |
| EP03 Android | US-006 | Como repartidor veo mis pedidos y ruta asignada | P0 | 4 | US-005 |
| EP03 Android | US-007 | Como repartidor cambio estado de mi entrega | P0 | 4 | US-006 |
| EP03 Android | US-008 | Como repartidor comparto ubicación durante ruta activa | P0 | 4 | US-006 |
| EP04 Optimización | US-009 | Como operador comparo orden de visita original con optimizado | P0 | 5 | US-005, Maps |
| EP04 Optimización | US-010 | Como repartidor visualizo las paradas en orden optimizado | P0 | 5 | US-009 |
| EP05 Métricas | US-011 | Como operador veo duraciones, km, % mejora, puntualidad | P0 | 6 | US-009, eventos |
| EP06 Asistente IA | US-012 | Como operador pido explicación fundamentada de resultados | P1 | 6 | US-011 |
| EP07 Resiliencia | US-013 | Como repartidor registro una incidencia | P1 | 6 | US-007 |
| EP07 Resiliencia | US-014 | Como repartidor sincronizo eventos pendientes tras reconectar | P1 | 6 | US-007 |
| EP08 Validación | US-015 | Como evaluador ejecuto piloto y exporto métricas comparables | P0 | 7 | US-011 |

**Estimación relativa provisional:** US-001..005=16 puntos; US-006..008=14; US-009..010=13; US-011=5; US-012=5; US-013..014=8; US-015=5. Total 66 puntos tentativos; no representa una velocidad garantizada.

## 14. Reglas de negocio e invariantes
- BR-01: sólo se asignan pedidos `PENDING`; cada pedido pertenece a máximo una ruta activa.
- BR-02: estados: `PENDING -> ASSIGNED -> IN_TRANSIT -> DELIVERED` o `FAILED`; `FAILED` exige motivo. No saltos salvo flujo de demo explicitado.
- BR-03: una ruta tiene `DRAFT -> PLANNED -> ACTIVE -> COMPLETED/CANCELLED`.
- BR-04: la ruta no puede iniciarse si faltan coordenadas válidas, paradas o repartidor.
- BR-05: el cálculo utiliza el mismo depósito y las mismas paradas para baseline y optimización.
- BR-06: no se presenta ahorro cuando no existe; `improvement_pct=(baseline_seconds-optimized_seconds)/baseline_seconds*100` si base > 0.
- BR-07: GPS requiere consentimiento vigente, ruta activa y usuario titular; incluir `captured_at` y `accuracy_m`.
- BR-08: eventos de actualización de entrega con `Idempotency-Key` para evitar duplicados.
- BR-09: no se admiten ubicaciones de pedidos fuera de área piloto o coordenadas inválidas.
- BR-10: el LLM no persiste mutaciones ni autoriza operaciones; el servidor revalida y acota su contenido.

## 15. Arquitectura lógica
Android Flutter y dashboard React -> HTTPS -> FastAPI monolito modular en Cloud Run (auth, pedidos, rutas, telemetría, métricas, IA) -> PostgreSQL. Servicio de rutas: Google Routes API `computeRouteMatrix` para tiempos/distancias -> OR-Tools para secuencia -> opcional `computeRoutes` para polilínea de visualización. IA: Gemini a través de backend con entrada estructurada y salida validada. Secret Manager para credenciales; logs y métricas; GitHub Actions para CI/CD. **La base de datos debe estar desplegada y provisionada aparte de Cloud Run**, que ejecuta contenedores sin persistencia local garantizada. Presupuesto y servicio PostgreSQL por definir.

**Protección:** TLS, tokens de corta duración, roles validados en servidor, secretos fuera del repositorio, claves de Maps restringidas según cliente/API, almacenamiento mínimo de GPS, expiración/eliminación periódica conforme política del piloto. No enviar domicilios ni coordenadas precisas a Gemini si basta con agregados. Revisar condiciones de almacenamiento y uso de resultados de Google Maps Platform antes de cachear matrices.

## 16. Diseño del optimizador
Entrada: `depot`, lista 1..10 `stops`, `baseline_order`, `travel_matrix_seconds[N][N]` y `distance_matrix_meters[N][N]`, con N=paradas+depósito. Permitir regreso a depósito como opción (por defecto: `return_to_depot=false`; ambas secuencias deben usar mismo valor). Obtener matrix Routes API o fixture versionada. Validar diagonales, valores nulos/no alcanzables, duplicados, IDs y consistencia del orden. Objetivo: minimizar tiempo total de viaje para 1 repartidor; `service_duration` se suma a ETA pero no altera el orden si es constante por parada y no hay ventanas. Tiempo máximo de búsqueda inicial 3 s, configurable. Si no existe solución válida, devolver `422 ROUTE_INFEASIBLE`, sin inventar ruta. Para rutas pequeñas, benchmarking por enumeración exhaustiva opcional en fixtures para detectar anomalías. OR-Tools devuelve soluciones factibles posiblemente no óptimas; reportar `solver_status`.

**Control de costos:** `computeRouteMatrix` cobra por elementos origen×destino; con 11 nodos, una matriz completa contiene 121 pares potenciales. Asegurar que la selección de campos, política de tráfico, cuotas y Términos de Maps están configurados adecuadamente; deshabilitar cálculos innecesarios y utilizar fixtures para pruebas.

## 17. Contrato HTTP interno (v1)
**Base:** `/api/v1`. Autenticación `Authorization: Bearer <token>`; contenido `application/json`, marcas temporales UTC ISO8601, UUID para IDs. Respuestas de error uniformes `{ "error": {"code":"...","message":"...","details":{}}, "request_id":"..." }`. `401` sin sesión, `403` rol no autorizado, `404` no existe/no visible, `409` conflicto de estado, `422` validación, `429` cuota, `503` servicio externo. Paginación `limit` máx 100 y `cursor` cuando aplique.

| Método | Ruta | Rol | Propósito | Historia |
|---|---|---|---|---|
| POST | `/auth/login` | Público | Token para demo, con credenciales | US-001 |
| GET | `/me` | Todos | Usuario y rol | US-001 |
| POST | `/orders` | Operador | Crear pedido | US-003 |
| GET | `/orders?status=&limit=&cursor=` | Operador | Consultar pedidos | US-004 |
| GET | `/orders/{order_id}` | Operador o titular | Detalle autorizado | US-004,006 |
| POST | `/routes` | Operador | Crear ruta borrador para repartidor | US-005 |
| POST | `/routes/{route_id}/orders` | Operador | Agregar pedidos pendientes | US-005 |
| POST | `/routes/{route_id}/optimize` | Operador | Calcular propuesta; comparación | US-009 |
| POST | `/routes/{route_id}/activate` | Operador | Publicar ruta planificada | US-006 |
| GET | `/routes/my/active` | Repartidor | Ruta propia | US-006 |
| GET | `/routes/{route_id}` | Operador/titular | Ruta y paradas | US-010 |
| PATCH | `/orders/{order_id}/status` | Repartidor titular | Estado de entrega | US-007 |
| POST | `/locations` | Repartidor titular | Enviar ubicación durante ruta | US-008 |
| GET | `/drivers/{driver_id}/latest-location` | Operador | Última ubicación con freshness | US-008 |
| GET | `/analytics/summary?from=&to=` | Operador | KPI y fuentes | US-011 |
| POST | `/ai/explain-route` | Operador | Explicación sin efectos | US-012 |
| POST | `/incidents` | Repartidor titular | Registrar incidencia | US-013 |
| GET | `/evaluation/runs/{run_id}` | Operador | Resultado de escenario piloto | US-015 |

### Ejemplos de payload y respuestas
**POST `/orders`**
```json
{
  "external_reference":"ORD-1001",
  "destination":{"address":"Dirección de prueba, Lima","latitude":-12.05,"longitude":-77.04,"place_id":null},
  "planned_service_seconds":180
}
```
`201`:
```json
{"id":"11111111-1111-4111-8111-111111111111","status":"PENDING","created_at":"2026-10-23T19:00:00Z"}
```
**POST `/routes`**
```json
{"driver_id":"22222222-2222-4222-8222-222222222222","depot":{"latitude":-12.06,"longitude":-77.05},"return_to_depot":false}
```
`201`: `{ "id":"33333333-3333-4333-8333-333333333333", "status":"DRAFT" }`

**POST `/routes/{route_id}/orders`**
```json
{"order_ids":["11111111-1111-4111-8111-111111111111"]}
```
`200`: `{ "route_id":"33333333-3333-4333-8333-333333333333", "stop_count":1 }`

**POST `/routes/{route_id}/optimize`**
```json
{"baseline_order":["11111111-1111-4111-8111-111111111111"],"matrix_source":"GOOGLE_ROUTES","max_solver_seconds":3}
```
`200` (valores exclusivamente ilustrativos):
```json
{
  "route_id":"33333333-3333-4333-8333-333333333333",
  "baseline":{"ordered_order_ids":["11111111-1111-4111-8111-111111111111"],"travel_seconds":840,"distance_meters":3100},
  "optimized":{"ordered_order_ids":["11111111-1111-4111-8111-111111111111"],"travel_seconds":840,"distance_meters":3100},
  "improvement_pct":0.0,
  "solver_status":"FEASIBLE",
  "matrix_version":"matrix-20261023-demo01",
  "evaluated_at":"2026-10-23T19:00:00Z"
}
```
Nota: los tiempos de servicio se reportarán por separado de `travel_seconds`; el mismo criterio aplica a ambas secuencias.

**PATCH `/orders/{order_id}/status`** con header `Idempotency-Key`:
```json
{"status":"DELIVERED","occurred_at":"2026-10-23T19:14:00Z"}
```
`200`: `{ "id":"11111111-1111-4111-8111-111111111111", "status":"DELIVERED" }`

**POST `/locations`**:
```json
{"route_id":"33333333-3333-4333-8333-333333333333","latitude":-12.051,"longitude":-77.041,"accuracy_m":12,"captured_at":"2026-10-23T19:12:00Z"}
```
`202`: `{ "accepted":true }`. Si consentimiento ausente o ruta inactiva: `403 LOCATION_NOT_ALLOWED`.

**GET `/analytics/summary`**:
```json
{"completed_orders":20,"avg_delivery_minutes":42.5,"on_time_rate":0.9,"route_improvement_pct":12.0,"basis":"OBSERVED_PILOT","period":{"from":"2026-10-20","to":"2026-10-23"}}
```

**POST `/ai/explain-route`**:
```json
{"route_id":"33333333-3333-4333-8333-333333333333","question":"¿Por qué esta secuencia?"}
```
`200`: `{ "summary":"La secuencia reduce el tiempo estimado de desplazamiento según la matriz proporcionada.","evidence":["baseline.travel_seconds","optimized.travel_seconds"],"limitations":["Estimación no equivale a tiempo observado"],"action_taken":false }`. Nunca ejecutar herramientas de escritura desde esta llamada.

## 18. Esquema de datos lógico (PostgreSQL)
Tablas y claves:
```sql
CREATE TABLE app_user (
 id UUID PRIMARY KEY, email TEXT UNIQUE NOT NULL,
 password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK (role IN ('OPERATOR','DRIVER')),
 is_active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE driver (
 id UUID PRIMARY KEY, user_id UUID NOT NULL UNIQUE REFERENCES app_user(id),
 display_name TEXT NOT NULL, gps_consent_at TIMESTAMPTZ,
 gps_consent_revoked_at TIMESTAMPTZ
);
CREATE TABLE delivery_order (
 id UUID PRIMARY KEY, external_reference TEXT UNIQUE NOT NULL,
 address_label TEXT NOT NULL, latitude NUMERIC(9,6) NOT NULL CHECK(latitude BETWEEN -90 AND 90),
 longitude NUMERIC(9,6) NOT NULL CHECK(longitude BETWEEN -180 AND 180),
 place_id TEXT, planned_service_seconds INTEGER NOT NULL DEFAULT 180 CHECK(planned_service_seconds >= 0),
 status TEXT NOT NULL CHECK(status IN ('PENDING','ASSIGNED','IN_TRANSIT','DELIVERED','FAILED')),
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(), completed_at TIMESTAMPTZ
);
CREATE TABLE delivery_route (
 id UUID PRIMARY KEY, driver_id UUID NOT NULL REFERENCES driver(id),
 status TEXT NOT NULL CHECK(status IN ('DRAFT','PLANNED','ACTIVE','COMPLETED','CANCELLED')),
 depot_latitude NUMERIC(9,6) NOT NULL, depot_longitude NUMERIC(9,6) NOT NULL,
 return_to_depot BOOLEAN NOT NULL DEFAULT FALSE,
 started_at TIMESTAMPTZ, ended_at TIMESTAMPTZ, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE route_stop (
 id UUID PRIMARY KEY, route_id UUID NOT NULL REFERENCES delivery_route(id),
 order_id UUID NOT NULL REFERENCES delivery_order(id), baseline_sequence INTEGER NOT NULL,
 optimized_sequence INTEGER, UNIQUE(route_id,order_id), UNIQUE(route_id,baseline_sequence)
);
CREATE TABLE order_status_event (
 id UUID PRIMARY KEY, order_id UUID NOT NULL REFERENCES delivery_order(id),
 actor_user_id UUID NOT NULL REFERENCES app_user(id), old_status TEXT NOT NULL,
 new_status TEXT NOT NULL, occurred_at TIMESTAMPTZ NOT NULL,
 idempotency_key TEXT NOT NULL, UNIQUE(actor_user_id,idempotency_key)
);
CREATE TABLE driver_location (
 id UUID PRIMARY KEY, driver_id UUID NOT NULL REFERENCES driver(id),
 route_id UUID NOT NULL REFERENCES delivery_route(id),
 latitude NUMERIC(9,6) NOT NULL CHECK(latitude BETWEEN -90 AND 90),
 longitude NUMERIC(9,6) NOT NULL CHECK(longitude BETWEEN -180 AND 180),
 accuracy_m NUMERIC(8,2) NOT NULL CHECK(accuracy_m >= 0),
 captured_at TIMESTAMPTZ NOT NULL, received_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE route_evaluation (
 id UUID PRIMARY KEY, route_id UUID NOT NULL REFERENCES delivery_route(id),
 baseline_seconds INTEGER NOT NULL, optimized_seconds INTEGER NOT NULL,
 baseline_meters INTEGER, optimized_meters INTEGER,
 improvement_pct NUMERIC(8,3), matrix_source TEXT NOT NULL,
 matrix_version TEXT NOT NULL, solver_status TEXT NOT NULL,
 metadata JSONB NOT NULL DEFAULT '{}', evaluated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE incident (
 id UUID PRIMARY KEY, order_id UUID NOT NULL REFERENCES delivery_order(id),
 driver_id UUID NOT NULL REFERENCES driver(id), incident_type TEXT NOT NULL,
 description TEXT, occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```
**Integridad adicional exigida en servicio/transacción:** prohibir que una orden esté en varias rutas no canceladas; transiciones de estado válidas; `optimized_sequence` único por ruta cuando no nulo (índice único parcial); índices para `route_stop(route_id)`, `delivery_order(status)`, `driver_location(driver_id,captured_at DESC)` y `route_evaluation(route_id)`. Para el piloto no se guardarán direcciones reales de clientes: usar datos sintéticos. Establecer política de borrado de ubicación antes de producción.

## 19. Criterios de aceptación y escenarios BDD
| AC | Historia | Given / When / Then | Tipo |
|---|---|---|---|
| AC-001 | US-001 | Dado repartidor autenticado, cuando consulta lista global de pedidos, entonces responde 403 | Seguridad |
| AC-002 | US-003 | Dada lat/lon inválida, cuando crea pedido, entonces responde 422 sin persistir | API |
| AC-003 | US-005 | Dado pedido ya asignado a ruta activa, cuando se intenta agregar a otra, entonces 409 | Integridad |
| AC-004 | US-006 | Dada ruta activa del usuario, cuando abre Android, entonces aparecen únicamente sus paradas | E2E |
| AC-005 | US-007 | Dado pedido asignado, cuando marca DELIVERED, entonces evento queda auditado una sola vez | Integración |
| AC-006 | US-008 | Dada ruta inactiva, cuando publica GPS, entonces 403 y no persiste | Privacidad |
| AC-007 | US-008 | Dado GPS de hace más de 2 min, cuando operador consulta, entonces aparece como `STALE` | UI |
| AC-008 | US-009 | Dadas N paradas distintas, cuando optimiza, entonces retorna exactamente esas N sin duplicados | Algoritmo |
| AC-009 | US-009 | Dada misma matriz y baseline, cuando calcula mejora, entonces el porcentaje coincide con fórmula | Unidad |
| AC-010 | US-009 | Dada matriz con nodo inaccesible, cuando optimiza, entonces 422 ROUTE_INFEASIBLE | Negativo |
| AC-011 | US-010 | Dada ruta planificada, cuando abre mapa, entonces respeta el orden optimizado publicado | E2E |
| AC-012 | US-011 | Dados eventos de entrega conocidos, cuando consulta dashboard, entonces KPI coincide con cálculo reproducible | Datos |
| AC-013 | US-012 | Dado payload sin mejora, cuando consulta Gemini, entonces no afirma ahorro positivo | IA |
| AC-014 | US-012 | Dada solicitud maliciosa para modificar pedidos, cuando usa explicación IA, entonces `action_taken=false` | Seguridad IA |
| AC-015 | US-015 | Dado piloto comparativo, cuando se generan resultados, entonces reporta muestra, método, fechas y limitaciones | Metodología |
| AC-016 | US-007 | Dado mismo Idempotency-Key reenviado, cuando aplica actualización, entonces se crea un único evento | Resiliencia |

## 20. Plan de pruebas y puertas de calidad
- **Unitarias:** lógica de estado, reducción porcentual, validaciones, secuenciación y simuladores de matriz.
- **Integración:** autenticación/RBAC, Postgres, idempotencia, mocks Routes/Gemini.
- **Contract tests:** payloads OpenAPI, esquema de respuesta y códigos de error.
- **E2E:** operador crea pedidos -> asigna -> optimiza -> activa -> repartidor confirma -> dashboard actualiza.
- **Seguridad/privacidad:** usuarios cruzados, ausencia de consentimiento, expiración tokens, no exposición de secretos.
- **Rendimiento:** CRUD p95 < 1s excluyendo APIs externas en entorno acordado; optimización para 10 paradas < 10s bajo fixtures; no garantizar esos objetivos sin prueba.
- **IA:** dataset de 20 casos de explicación (ahorro positivo, cero, negativo, faltantes, inyección, pregunta fuera de alcance); aspiración: 100 % de respuestas sin acción de escritura y 0 KPI inventados en test.
- **Salida de semana:** sin fallos severidad crítica, P0 pasadas, regresión documentada y PR revisado.

## 21. Protocolo de evaluación del -20 %
**Definición primaria:** tiempo promedio observado por entrega durante la jornada, desde salida de depósito hasta cierre de última entrega, dividido entre entregas completadas. Registrar por recorrido; distinguir tiempos de desplazamiento vs. servicio y esperas.
**Diseño sugerido:** recorridos A (orden manual fijado antes del cálculo) y B (orden optimizado) sobre conjuntos y franjas comparables; mismo depósito, número de paradas, clase de vehículo y reglas de servicio. No realizar entregas duplicadas reales; usar rondas equivalentes o simulación controlada cuando no exista operación real. Guardar IDs anonimizados, timestamps, matriz inicial, orden base y orden optimizado.
**Métricas secundarias:** tiempo estimado en matriz, kilómetros totales, puntualidad, minutos de retraso, tasa de entrega, calidad GPS, latencia de optimización, costo estimado/ejecución.
**Cálculo:** `(T_base - T_piloto) / T_base * 100`; por ruta y agregado ponderado por entregas, con unidad claramente declarada. Mostrar n, media, mediana, dispersión, condiciones y sesgos. Simulaciones se etiquetan como tales y **no prueban** una reducción real observada.
**Criterio:** meta -20 %; no confundir benchmark de rutas con mejora de negocio demostrada.

## 22. Backlog de trabajo por semana — aceptación y salida
| Semana | Historias / trabajos | Dependencias | Artefacto de salida / gate |
|---|---|---|---|
| S1 | Entrevistas simuladas, Business Case preliminar, proceso AS-IS/TO-BE, métricas, Charter, EP y US | Ninguna | G1: Charter y alcance P0 aprobados |
| S2 | Wireframes Android/dashboard, ERD, OpenAPI, repo, CI, claves y cuotas, fixtures de rutas | G1 | G2: SPEC y prototipo revisados; prueba API mock |
| S3 | US-001..005, migraciones DB, APIs de pedidos/rutas, RBAC, seeds | G2 | G3: pedidos asignables y tests API |
| S4 | US-006..008, Flutter, navegación, GPS, estado, conectividad básica | G3 | G4: recorrido digital básico en Android |
| S5 | US-009..010, matriz Routes, OR-Tools, validación, benchmark y mapas | G4 | G5: comparación estable y reproducible |
| S6 | US-011..012, métricas, asistente consultivo, US-013/014 si hay holgura, hardening | G5 | G6: demo integral y pruebas E2E |
| S7 | US-015, piloto, dashboard de resultados, SQA, riesgos, Canvas, VAN/TIR con supuestos, sustentación | G6 | G7: evidencia y paquete académico final |

**Ruta crítica:** auth -> pedidos -> asignación -> Android -> matriz -> optimización -> dashboard -> piloto. **Recorte preventivo:** primero eliminar US-013, US-014, refinamientos de IA o UI; preservar datos, optimización, telemetría y evaluación.

## 23. Repo recomendado
```
smartroute-ai/
  README.md
  docs/
    project-charter.md
    business-case.md
    canvas.md
    risks.md
    quality-plan.md
    stakeholders.md
    pilot-protocol.md
  specs/
    SPEC.md
    requirements/epics.md
    api/openapi.yaml
    data/schema.sql
    acceptance/acceptance.feature
  apps/mobile/       # Flutter Android
  apps/dashboard/    # React
  services/api/      # FastAPI modular monolith
  services/routing/  # OR-Tools & Routes adapter
  services/ai/       # Gemini readonly
  tests/unit/
  tests/integration/
  tests/e2e/
  tests/fixtures/
  infra/
  .github/workflows/
```

## 24. Dependencias y decisiones abiertas
1. Equipo disponible y horas por semana; reparto de responsabilidades.
2. Dispositivo Android y método de piloto (campo real o simulación).
3. Presupuesto para Maps Platform, Gemini, Cloud Run y PostgreSQL.
4. Política de localización, consentimiento y tratamiento de datos sintéticos.
5. Entorno PostgreSQL administrado o alternativo para demo; Cloud Run no provee DB persistente.
6. Reglas específicas de rutas: retorno a depósito, horarios y tiempos de servicio.
7. Línea base de negocio validada y tamaño de muestra realista.
8. Pricing actualizado al hacer Business Case, sin presupuestar con valores supuestos como reales.

## 25. Bibliografía técnica verificada
- Google Maps Platform Routes API: https://developers.google.com/maps/documentation/routes/reference/rest
- Google Maps Platform, uso y cobro: https://developers.google.com/maps/documentation/routes/usage-and-billing
- OR-Tools, Vehicle Routing: https://developers.google.com/optimization/routing
- Gemini generateContent: https://ai.google.dev/api/generate-content

**Nota de alcance:** La v1.0 fija contratos funcionales conceptuales y esquema lógico. El fichero OpenAPI 3.x ejecutable, migraciones SQL completas, arquitectura de despliegue y cifras del Business Case serán siguientes artefactos derivados; no están falsamente declarados como implementados.