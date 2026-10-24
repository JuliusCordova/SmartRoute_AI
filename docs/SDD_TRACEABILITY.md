# Trazabilidad integral — fuente de verdad de ingeniería
| Causa | Necesidad | Objetivo | Historias | Requisito | Componente | Aceptación | KPI |
|---|---|---|---|---|---|---|---|
| CR2 datos dispersos | NEC-01 | OG | US-003…005 | RF-02…04 | Orders + PostgreSQL | AC-002,003 | coordenadas válidas |
| CR1 y CR5 ruteo manual/tráfico | NEC-02 | OE1, OE2 | US-009,010 | RF-08 | Maps Adapter + OR-Tools | AC-008…011 | min/entrega, km/ruta |
| CR3 falta seguimiento | NEC-03 | OE3 | US-006…008 | RF-05…07 | Mobile + Tracking | AC-004…007,016 | trazabilidad y puntualidad |
| CR4 no hay métricas | NEC-04 | OE1–OE3 | US-011,015 | RF-09,12 | Analytics + pilot export | AC-012,015 | 3 KPI observados |
| R05 alucinación IA | NEC-05 | OG | US-012 | RF-10 P1 | Gemini/Vertex read-only | AC-013,014 | 0 inventados |

## Evidencia: condición para marcar completado
Un control Capstone no se valida por existir documentación. Requiere PR/commit, captura o reporte de prueba ejecutada, resultados reproducibles y sección final del informe. Ver [matriz 36 controles](Matriz_Maestra_Capstone_SDD.md). El avance de campo I ya redacta Pareto/Ishikawa/5 porqués, cinco NEC, seis ADR, siete criterios de selección y simulación inicial; aún declara faltantes en evidencia primaria, SQA, despliegue y piloto.

## Regla de control
Cada PR debe referir `US-`, `RF-`, `AC-`, `NEC-`, ruta de evidencia y efecto sobre OE1/2/3. Diferenciar `DESIGN`, `IMPLEMENTED`, `TESTED`, `DEPLOYED`, `OBSERVED`; el estado actual de estas nuevas specs es `DESIGN`. El documento de 50 páginas es insumo del equipo, no se publica automáticamente como archivo fuente sin controlar su licencia y datos.
