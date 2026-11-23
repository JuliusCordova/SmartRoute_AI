# Trazabilidad integral — fuente de verdad de ingeniería

> **Actualización de estado, 23/11/2026:** se ha ejecutado un segundo recorrido QA de **5 paradas** con GPS emulado y cierre verificado en Firestore. Las filas históricas del 22/11 se conservan; véase la **adenda** al final y el [acta formal SQA](evidence/ACTA_CORTE_FORMAL_SQA_E2E_2026-11-23.md). **TESTED QA ≠ OBSERVED en campo**.

| Causa | Necesidad | Objetivo | Historias | Requisito | Componente | Aceptación | KPI |
|---|---|---|---|---|---|---|---|
| CR2 datos dispersos | NEC-01 | OG | US-003…005 | RF-02…04 | Orders + Firestore Standard | AC-002,003 | coordenadas válidas |
| CR1 y CR5 ruteo manual/tráfico | NEC-02 | OE1, OE2 | US-009,010 | RF-08 | Maps Adapter + OR-Tools | AC-008…011 | min/entrega, km/ruta |
| CR3 falta seguimiento | NEC-03 | OE3 | US-006…008 | RF-05…07 | Mobile + Tracking | AC-004…007,016 | trazabilidad y puntualidad |
| CR4 no hay métricas | NEC-04 | OE1–OE3 | US-011,015 | RF-09,12 | Analytics + pilot export | AC-012,015 | 3 KPI observados |
| R05 alucinación IA | NEC-05 | OG | US-012 | RF-10 P1 | Gemini/Vertex read-only | AC-013,014 | 0 inventados |

## Evidencia: condición para marcar completado
Un control Capstone no se valida por existir documentación. Requiere PR/commit, captura o reporte de prueba ejecutada, resultados reproducibles y sección final del informe. Ver [matriz 36 controles](Matriz_Maestra_Capstone_SDD.md). El avance de campo I ya redacta Pareto/Ishikawa/5 porqués, cinco NEC, seis ADR, siete criterios de selección y simulación inicial; aún declara faltantes en evidencia primaria, SQA, despliegue y piloto.

## Regla de control
Cada PR debe referir `US-`, `RF-`, `AC-`, `NEC-`, ruta de evidencia y efecto sobre OE1/2/3. Diferenciar `DESIGN`, `IMPLEMENTED`, `TESTED`, `DEPLOYED`, `OBSERVED`; los artefactos originales describían `DESIGN`, pero la ruta QA del 22/11/2026 está `TESTED` en móvil y operador y `DEPLOYED` sólo en revisiones etiquetadas sin tráfico principal; no se acreditan KPIs `OBSERVED` de campo. El documento de 50 páginas es insumo del equipo, no se publica automáticamente como archivo fuente sin controlar su licencia y datos.


## Trazabilidad de implementación E2E — 22/11/2026

**Referencia de estados:** `DESIGN` propuesta → `IMPLEMENTED` código disponible → `TESTED` funcional validado → `DEPLOYED` revisión QA etiquetada → `OBSERVED` datos de operación real (este último **no** alcanzado). No confundir `TESTED` con aceptación de rúbrica ni `DEPLOYED QA` con producción.

| Necesidad | Historia implementada | Contrato técnico | Evidencia/criterio | Estado |
| --- | --- | --- | --- | --- |
| NEC-01 pedidos/geo | US-003/004 | `POST/GET /api/v1/orders` | Capturas del operador; pedidos sintéticos en la ruta E2E | TESTED QA |
| NEC-02 ruteo optimizado | US-009/010 | `POST /api/v1/optimization/preview`; `POST /api/v1/optimized-routes` | 6 paradas, matriz ORS estimated, secuencia guardada, 15,84 % estimado | TESTED QA; beneficio OBSERVED pendiente |
| NEC-01/03 asignación | **US-IMP-011** (no US-V1-011) | `POST /api/v1/optimized-routes/{id}/assign-driver` | AC-IMP-011; ruta asignada a QA, sin afectar Manuel | TESTED QA |
| NEC-03 ejecución de ruta | **US-IMP-012** (no US-V1-012) | `POST /api/v1/driver/me/route/start` | AC-IMP-012; confirmación de inicio y ruta ACTIVE | TESTED QA |
| NEC-03 estados entrega | **US-IMP-013** (relacionada pero no idéntica a US-V1-013) | `POST /api/v1/driver/me/route/stops/{id}/deliver\|fail` | AC-IMP-013; 5 DELIVERED + 1 FAILED | TESTED QA |
| NEC-03 cierre | **US-IMP-014** (no US-V1-014) | `POST /api/v1/driver/me/route/complete` | AC-IMP-014; ruta COMPLETED v10 en operador | TESTED QA |
| NEC-03 ubicación GPS / resiliencia offline | US-V1-008 y US-V1-014 | No validado en flujo actual | Faltan consentimiento, captura GPS observada y reintentos offline | PENDIENTE |
| NEC-04 métricas de impacto | US-V1-011 y US-V1-015 | Comparación estimada disponible; export piloto no validado | OE1 -20% y puntualidad requieren línea base y muestras reales | PENDIENTE |
| NEC-05 IA | US-V1-012 | Gemini consultivo sólo diseño | No se validó API/UI LLM en esta prueba | PENDIENTE |

**Referencia de test:** `TC-E2E-QA-20261122-01` y [acta](evidence/E2E_OPERADOR_ANDROID_QA_2026-11-22.md). El reporte conserva los IDs técnicos originales como alias de implementación y mantiene v1 como baseline inmutable.


---

## Adenda de trazabilidad — segundo E2E QA, 23/11/2026

**Caso:** `TC-E2E-QA-20261123-02`; **ruta** `fb413b71-c963-570f-be61-500e9eadfb7b`. Evidencia con IDs **E23-01…E23-14** en [acta formal](evidence/ACTA_CORTE_FORMAL_SQA_E2E_2026-11-23.md).

| Necesidad / control | Historia / implementación | Contrato(s) observado(s) | Aceptación/evidencia | Estado y alcance |
| --- | --- | --- | --- | --- |
| NEC-01 pedidos | US-V1-003/004 | API pedidos + UI operador | E23-01/02, preparación de cinco pedidos, filtros operador | TESTED QA; negativos pendientes |
| NEC-02 optimización | US-V1-009/010 | preview OR-Tools/ORS → optimized-routes → lectura DRIVER | E23-02; 48,43→41,68 km; 71→61 min; 14,59 % estimado | TESTED QA; OE1/OE2 OBSERVED pendiente |
| NEC-03 asignación | US-V1-005 / US-IMP-011 | assign-driver | E23-01, E23-12; conductor reservado y luego disponible | TESTED QA |
| NEC-03 inicio | US-IMP-012 | POST `/api/v1/driver/me/route/start` | E23-03/04, confirmación y ACTIVE | TESTED QA |
| NEC-03 entrega | US-V1-007 / US-IMP-013 | POST deliver/fail | E23-07/08/09; 4 DELIVERED, 1 FAILED; 2 GET REST directos | TESTED QA; 3 GET directos pendientes |
| NEC-03 GPS | **US-V1-008** | POST `/api/v1/driver/me/location`; GET Firestore REST `driver_last_locations` | E23-05/06; ubicación consentida del emulador, 5 m, documento HTTP 200 | **TESTED QA SIMULADO**, **no** OBSERVED de terreno |
| NEC-03 cierre y privacidad | US-IMP-014 | POST complete + Firestore readbacks | E23-10…13; COMPLETED, available=true, assignment 404, history 200, GPS 404 | **PASS E2E QA** |
| NEC-04 KPI/piloto | US-V1-011/015 | Dashboard y export | Solo KPIs estimated y 2 ejecuciones sintéticas independientes | PARCIAL/PENDIENTE; sin muestras comparables ni puntualidad OBSERVED |
| NEC-05 Gemini | US-V1-012 P1 | Gemini consultivo | No se probó en segundo E2E | DESIGN/IMPLEMENTED parcial según módulo; no TESTED |

**Reglas de trazabilidad:** no mezclar US-IMP-012/013/014 con historias baseline US-V1-012/013/014; distinguir prueba técnica del laboratorio de aceptación docente. La matriz P0 vigente al corte es [10 aceptadas, 1 parcial, 1 pendiente](evidence/MATRIZ_ACEPTACION_P0_2026-11-22.md). No reutilizar rutas COMPLETED para pruebas mutantes.
