# Trazabilidad integral — fuente de verdad de ingeniería
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
