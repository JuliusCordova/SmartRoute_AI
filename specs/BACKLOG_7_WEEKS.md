# Backlog de ejecución PA-SDD — siete semanas (Firestore Standard)
**Fuente operativa:** [Plan maestro de desarrollo](../docs/PLAN_DESARROLLO_7_SEMANAS.md). Este backlog reemplaza el cronograma anterior que mencionaba PostgreSQL. **No hay funcionalidades P0 desplegadas aún.**

| Semana | US / objetivo | Entregable demostrable | Evidencia de gate |
|---|---|---|---|
| S1 | Fundación, auth y emulador | CI FastAPI, Firestore Emulator, definición de OIDC y baseline | tests y fixtures sintéticos, SPEC revisada |
| S2 | US-003/004 + US-001/002 | POST/GET pedidos en Firestore con RBAC | AC-001/002 + tests emulador |
| S3 | US-005, ruta draft | Asignación y transacciones Firestore, staging Cloud Run autorizado | AC-003 + smoke de API y URL |
| S4 | US-006/007/008 | Flutter consulta ruta, estado, idempotencia y GPS | AC-004/005/006/007/016 |
| S5 | US-009/010 | Maps matriz + OR-Tools + publicar ruta | AC-008/009/010/011 |
| S6 | US-011 (P0), US-012 (P1) | React KPIs; Gemini solo si P0 verde | AC-012; AC-013/014 P1 |
| S7 | US-015 + Capstone | Export piloto + evidencia, OneDrive y video | AC-015; KPI, matriz UPN, release gate |

## Priorización
P0: US-001…011 y US-015. P1: US-012…014. El asistente Gemini del producto no bloquea el flujo mínimo funcional. El Master y especialistas SDD sirven al proceso de ingeniería, sin requerir servicios ADK independientes para iniciar.

## Definition of Ready
Historia identificada, NEC y OE vinculados, RF/AC verificables, fixtures sintéticos, dependencia, dueño (por asignar), riesgos y presupuesto del servicio externo.

## Definition of Done
Código + pruebas reales + verificación de permisos + revisión humana de PR + trazabilidad actualizada. Para declarar DEPLOYED exigir URL, revisión/commit, smoke e instrucciones de rollback. No igualar diseño con implementación.

## Kanban
Backlog → Ready → Development → Review → Test → Done. Ningún ticket se cierra sin evidencia. El documento detallado registra roles, riesgos, costos, roadmap semanal y estrategia académica.
