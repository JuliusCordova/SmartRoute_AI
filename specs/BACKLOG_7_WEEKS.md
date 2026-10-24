# Backlog PA-SDD · siete semanas · cuatro integrantes
| Semana | Slice/entregable | Criterio de gate | Prioridad |
|---|---|---|---|
| S1 | caso, observación primaria, hipótesis, línea base y backlog | G1 Charter y P0 congelado; datos sintéticos marcados | P0 |
| S2 | ERD, OpenAPI, UI, ADR, fixtures, CI | G2 spec/contratos/mocks revisados | P0 |
| S3 | Auth + orders + routes draft + PostgreSQL | G3 API y pruebas de permisos/duplicados | P0 |
| S4 | Flutter ruta + eventos estado + consentimiento/GPS | G4 flujo end-to-end Android verificable | P0 |
| S5 | Routes API + solver OR-Tools + evaluaciones | G5 baseline vs optimize reproducible y ruta no factible | P0 |
| S6 | KPI dashboard + Vertex Gemini consultivo, integración y seguridad | G6 demo integrada y golden set IA | P0/P1 |
| S7 | piloto A/B 15+15 o simulación diferenciada, discusión y video | G7 informe, evidencia, veredicto ético | P0 |

## Reglas de ejecución
- 4 estudiantes × 10 h/sem × 7 sem = 280 horas **supuestas**, confirmar con equipo.
- Priorizar P0 (US-001 a 011 y US-015) antes de P1 (US-012 a 014). La IA P1 no bloquea la investigación principal.
- Un incremento semanal debe tener spec→código→test→evidencia; nunca afirmar despliegue antes de probar.
- Tablero Kanban Backlog → Ready → Development → Review → Test → Done.
- Gate de definición de historia: ID, actor, propósito, criterio de aceptación, datos/fixture, error handling, responsable.
- Gate de terminado: PR revisado, tests verdes, RBAC/política validada, métricas y evidencia; impactos en documento actualizados.
- Ruta crítica: auth → orders → routes → Android → matrix → solver → dashboard → piloto.
