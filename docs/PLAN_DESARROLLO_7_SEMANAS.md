# Plan maestro de desarrollo — SmartRoute AI Capstone (7 semanas)
**Versión:** 1.0 · **Estado:** planificado, no ejecutado · **Nube:** GCP · **Persistencia vigente:** Firestore Standard (Native mode).
**Fuentes de verdad:** [SPEC](../specs/SPEC.md), [ADR Firestore](FIRESTORE_STANDARD_MVP.md), [arquitectura GCP](ARCHITECTURE_GCP.md), [criterios BDD](../tests/acceptance.feature), [matriz UPN](Matriz_Maestra_Capstone_SDD.md), [AGENTS.md](../AGENTS.md).
**Método:** [DevPattern PA-SDD / Assisted Agentic SDLC](https://github.com/JuliusCordova/DevPattern/tree/main/patterns/assisted-agentic-sdlc).
**Duración:** 7 semanas relativas a la fecha de inicio aprobada; **no implica fechas de calendario comprometidas**. Hipótesis de capacidad: 4 integrantes × 10 h/semana × 7 = 280 horas; confirmar disponibilidad. Responsable humano por asignar.

## Resultado verificable al final
Una app Flutter Android y un dashboard React consumiendo FastAPI desplegado en Cloud Run, con autenticación, Firestore, registro y asignación de 5–10 pedidos en una ruta, estado de entregas y GPS limitado a ruta activa/consentimiento, Google Routes API + OR-Tools, KPIs y exportación de datos etiquetados. Gemini en Vertex AI es **P1 y consultivo** (explica solo KPI verificados; sin acciones de escritura). No se promete una mejora real del 20% antes de observarla.

## Reglas de arquitectura y ahorro
- Una sola API modular FastAPI y una base Firestore Standard, Cloud Run con min instances = 0; sin Cloud SQL, BigQuery, Redis, GKE, GraphRAG ni infraestructura adicional de agentes en el MVP.
- El **desarrollo asistido** utiliza roles SDD, Architect, Backend, Frontend, QA y DevOps; esto no exige desplegar un Master ADK. El agente **del producto** Gemini es P1, separado del sistema de desarrollo.
- Android y React solo consumen API; no Firebase Admin SDK ni claves de servicio en cliente. Firestore Rules deny-all para acceso cliente y acceso servidor IAM mínimo; RBAC/ownership en FastAPI.
- Transacciones Firestore para asignación y evento de estado idempotente; probar dos clientes concurrentes. Mocks/emulador para CI. Último GPS por conductor, muestreado durante ruta ACTIVE y consentimiento vigente.
- Google Routes API se invoca solo por optimización solicitada, con límites de 10 paradas, cuotas y control de respuestas; OR-Tools calcula la secuencia de modo determinista.
- Gemini únicamente bajo solicitud explícita del usuario, con JSON agregado sin PII, golden set y límite de gasto. API/ML no entrenado para ETA durante las 7 semanas.
- Credenciales por WIF/identidades gestionadas; presupuestos y alertas no impiden automáticamente sobregastos. Recursos GCP solo tras revisión humana.

## Gantt de entregas: incrementos con gates de evidencia

| Semana | Objetivo / vertical slice | Historias y tareas principales | Evidencia de salida obligatoria | Gate |
|---|---|---|---|---|
| **S1** | **Foundation verificable**: API health en CI y entorno dev de Firestore Emulator, especificación alineada | US-001/002 diseño auth, RF-01, fixture sintético, scripts bootstrap, roles IAM propuestos, matriz T1 y línea base/protocolo; resolver inconsistencias v1 | PR revisado; pruebas /health y /ready ejecutadas; emulador arrancable; evidencia de datos sintéticos y aprobación de especificación | G0–G1 |
| **S2** | **Pedido creado y consultado (E2E)** | US-003/004; FastAPI POST/GET orders, Pydantic, Firestore repository + emulator, paginación y autenticación RBAC (operador) | AC-001/002: pruebas automatizadas + demo FastAPI→Firestore; CI verde; lectura/escritura medidas | G2 |
| **S3** | **Asignación transaccional y ruta borrador** | US-005, US-009 (draft), RF-04; driver, route, stops, transacciones concurrentes; habilitar staging Cloud Run + Firestore *tras aprobación* | AC-003: solo una asignación confirmada entre dos intentos; smoke con commit y URL, coste observado | G3 |
| **S4** | **Flutter flujo repartidor** | US-006/007/008; login, mi ruta, estados, idempotency key, GPS consentido y solo ACTIVE, última ubicación | AC-004/005/006/007/016, tests emulator; demostración Android→Cloud Run→Firestore | G4 |
| **S5** | **Optimización medible** | US-009/010; adapter Google Routes API con fixtures/timeout, solver OR-Tools, baseline y comparación homogénea, activación de ruta | AC-008/009/010/011, matrices sintéticas reproducibles, no duplicados, fallback y logs | G5 |
| **S6** | **Dashboard de KPIs y ensayo integrado** | US-011; React panel pedidos/rutas/KPIs, dataset exportable; US-012 Gemini A1 **solo si P0 está verde** | AC-012, regresión P0, seguridad, 20 casos golden Gemini si se habilita, costos de Maps/Gemini | G6 |
| **S7** | **Piloto, sustentación y paquete final** | US-015; exportación con procedencia, ejecución protocolo 15+15 solo si se obtienen observaciones; ética, informe UPN, OneDrive y video <10 min | AC-015, 3 KPI con n/origen, porcentaje P0 probado, límites, URL demo y rollback, informe/actas; si solo simulación, declararlo | G7 |

**Restricción de fechas:** etapas condicionadas por gates: si S2 no prueba autorización y persistencia, no considerar S3 completada. P1 no retrasa el P0. Algunos gates G0–G7 son hitos de proyecto; no confundir con G0–G5 de patrón DevPattern usado para promoción tecnológica.

## Backlog por épica y criterio de terminado
| Épica | US | Prioridad | Dependencias | Criterio de aceptación mínimo |
|---|---|---|---|---|
| Identidad y control | US-001–002 | P0 | emisor OIDC y configuración | JWT iss/aud validado, OWNER/ROLE enforce API, AC-001 |
| Pedidos | US-003–004 | P0 | Firestore, identidad | POST/GET paginado, sin persistir coordenadas inválidas, AC-002 |
| Asignación | US-005 | P0 | pedidos, conductor, rutas | Transacción: conflicto 409, AC-003 |
| Ruta móvil y eventos | US-006–008 | P0 | asignación, Android | ownership, idempotencia, GPS ACTIVE+consent, AC-004–007/016 |
| Optimización | US-009–010 | P0 | Routes API, OR-Tools, rutas | secuencia contiene exactamente paradas, error de ruta imposible, AC-008–011 |
| Reportes | US-011,015 | P0 | eventos y métricas | cálculo repetible, exportación con data_origin, AC-012/015 |
| Gemini explicación | US-012 | P1 | KPIs validados | sin KPIs inventados, 0 tool writes, 20 golden tests, AC-013/014 |
| Incidencias/offline | US-013–014 | P1 | Android/transacciones | definir nuevos AC y tests antes de construir |

**Definición de Done:** especificación y ADR alineados, PR con trazabilidad NEC→OE→US→RF→AC, código funcional, test ejecutado (con salida verificable), seguridad/privacidad revisadas, CI verde y evidencias enlazadas. Solo llamar *desplegado* a un servicio cuando haya revisión, URL Cloud Run, smoke real y rollback registrado.

## Asignación propuesta de trabajo (ajustable según equipo)
| Rol de trabajo | Responsabilidad principal | Entregables | Aprobación |
|---|---|---|---|
| Integrante A — líder técnico / SDD | planificación, calidad SPEC, integración, PR | requisitos, trazabilidad, gates | revisión colectiva |
| Integrante B — backend/cloud | FastAPI, Firestore, IAM, deploy | API + repositorios + pruebas | QA + reviewer |
| Integrante C — móvil | Flutter, estados, GPS, UX | APK / demo + pruebas | QA + reviewer |
| Integrante D — web/analítica/IA | React, KPIs, export, Gemini P1 | dashboard + pruebas + evals | QA + reviewer |
| QA cruzado | integrantes distintos del autor revisan pruebas | reportes y defectos | no autoaprobar |
**Los responsables personales están pendientes de acuerdo del grupo; los roles de agentes de IA son asistentes y no sustituyen accountability humano.**

## Estrategia de GitHub / ejecución asistida
1. Abrir Issue por `US-`, con NEC/OE/RF/AC, dependencias y estimación. Etiquetas propuestas: `P0`, `P1`, `backend`, `mobile`, `web`, `cloud`, `qa`, `academic`, `blocked`.
2. Rama `feat/US-003-orders-create` y PR por incremento; no escribir directo a main. `AGENTS.md` obliga a leer SPEC/contratos primero.
3. Desarrollo asistido: SDD convierte historia en prueba; Architect revisa puertos y ADR; Builder implementa; QA evalúa; DevOps documenta imagen/deploy. PR requiere humano.
4. CI ejecuta pytest y Docker build; al incorporar Flutter/React, agregar sus test/lint/build. Hacer gate de seguridad, permisos y dependencias antes de despliegue.
5. Emulador y mocks son por defecto, sin gasto GCP. Staging solo por autorización humana; registrar costo y ejecutar smoke. Mantener rollback documentado.

## Riesgos, disparadores y mitigación
| Riesgo | Disparador | Mitigación verificable |
|---|---|---|
| Costo inesperado Maps/Vertex | optimizaciones o tokens fuera de control | cuotas, máximo 10 paradas, presupuestos y cuenta piloto |
| Firestore lecturas excesivas | polling/listeners o queries sin índice | consulta por ID, paginación, conteo de reads por demo |
| Doble asignación / estados repetidos | dos peticiones concurrentes | transacción Firestore e idempotency documentado y test AC-003/016 |
| Falta de datos reales | línea base del piloto no disponible | distinguir synthetic/estimated/observed y documentar autorización docente |
| App Android retrasada | S4 sin base de API usable | contract-first + mock y flow mínimo sin IA |
| Servicios GCP no configurados | acceso/IAM/billing no habilitados | CI local/emulador; check de preparación y aprobación GCP |
| Alcance agéntico excesivo | P1 bloquea P0 | Gemini solo en S6 si P0 está verde, ADK no obligatorio |

## Costo: estrategia de control
No prometer costo cero. Presupuesto monetario y región deben quedar aprobados antes del staging. Capturar consumo real del periodo de piloto: Firestore reads/writes/storage, Cloud Run requests/CPU, Google Routes requests, Gemini tokens, logs/egress. Optar por una sola base Firestore; Cloud Storage solo si exportación lo exige; BigQuery y Cloud SQL NO forman parte del despliegue piloto.

## Plan de investigación y evaluación UPN (en paralelo, sin suplantar construcción)
S1 define baseline, 5 evidencias y técnicas Pareto/Ishikawa/5 porqués; S2 compara alternativas y diseño; S3–S5 deja evidencia de implementación y testing; S6 prepara validación; S7 reporta resultados de tiempo, distancia y puntualidad, impactos y ética. La simulación preliminar de 30 rutas/233 entregas NO es piloto real. Si el plan cuasiexperimental 15+15 no puede ejecutarse, documentar limitaciones y no inventar resultados. El repositorio GitHub es fuente técnica, y los enlaces institucionales OneDrive se completan conforme las reglas académicas.

## Primer incremento inmediato (Ready → Development)
**US-003 / US-004:** implementar `POST /api/v1/orders` y `GET /api/v1/orders` con repositorio Firestore, validación de lat/lng, datos sintéticos, rol OPERATOR, pruebas unitarias y de integración con emulador, y medición de lecturas. Precondiciones: decidir emisor OIDC, variables `GCP_PROJECT` y `FIRESTORE_EMULATOR_HOST`, convención de estados y data_origin. Evidencia de aceptación AC-001/002. No crear recursos GCP sin aprobación.

## Registro de inicio de ejecución — incremento US-003 / US-004

Se creó la primera rama funcional de backend `feat/US-003-004-firestore-orders-api`: modelos/validación, autenticación Firebase con roles en Firestore, adaptador de pedidos, endpoints POST/GET, pruebas unitarias y contrato de paginación actualizado. **Estado: IMPLEMENTED (código) + UNIT TESTED local 5/5**; integración con Firestore Emulator y ejecución de GitHub Actions pendientes de confirmación. No equivale a S2 completada ni a DEPLOYED. Evidencias de CI y cloud requieren su propio reporte reproducible.
