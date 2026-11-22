# SmartRoute AI — US-004 y Centro de Control Ejecutivo

**Fecha:** 22/11/2026. **Estado:** código frontend desarrollado; pruebas E2E del navegador contra staging pendientes. No se declara aceptación formal ni despliegue a producción.

## US-V1-004 — Filtros de pedidos

- Filtra Todos, PENDING, ASSIGNED, IN_TRANSIT, DELIVERED y FAILED.
- Busca simultáneamente por dirección, ID de pedido o ID de ruta; combina búsqueda y estado.
- Informa cuántos pedidos están visibles frente al total consultado y muestra estado vacío.
- No modifica pedidos; sólo se pueden seleccionar pedidos PENDING para optimizar.
- Consulta GET /api/v1/orders con paginación por cursor (50 por página, máximo 10). Si hay más páginas, informa que la cobertura es parcial.

## Dashboard ejecutivo — US-V1-011 parcial

- Portada oscura de centro de control con diseño responsive, 4 tarjetas KPI, barras y mapa OSM ya existente.
- Pedidos y rutas consultados, filtro interactivo de estados de ruta.
- Efectividad = DELIVERED / (DELIVERED + FAILED) × 100; sin denominador se muestra un guion.
- Mejora estimada = (suma baseline_seconds − suma optimized_seconds) / suma baseline_seconds × 100 sobre rutas con baseline positiva. Se pondera por tiempo; nunca se presenta como ahorro real observado.
- Distribución de pedidos por estado calculada exclusivamente sobre registros recuperados.
- No presume GPS real, puntualidad, tiempos observados o series temporales inexistentes.

## Criterios de aceptación y pruebas

| ID | Acción | Resultado esperado | Estado |
| --- | --- | --- | --- |
| TC-US004-01 | Filtrar cada estado | Sólo pedidos coincidentes | Test unitario añadido; E2E pendiente |
| TC-US004-02 | Buscar texto e ID con filtro | Intersección de predicados | Test unitario añadido; E2E pendiente |
| TC-US004-03 | Listar paginación >1 | Leer páginas o advertir cobertura parcial | Test unitario añadido; E2E pendiente |
| TC-US004-04 | Filtrar rutas por estado | Sólo rutas coincidentes | Test unitario añadido; E2E pendiente |
| TC-EXE-01 | KPI entregadas / resueltas | Porcentaje correcto sin dividir por cero | Test unitario añadido; E2E pendiente |
| TC-EXE-02 | KPI mejora estimada | Cálculo agregado ponderado correcto | Test unitario añadido; E2E pendiente |
| TC-EXE-03 | Sin datos cargados | Cero para conteos; guion para ratios | Test unitario añadido; E2E pendiente |

## Cambios de código

- apps/operator-web/src/operations.js — filtros, métricas y paginación.
- apps/operator-web/src/main.jsx — dashboard y filtros integrados.
- apps/operator-web/src/style.css — diseño ejecutivo responsive.
- apps/operator-web/tests/operations.test.js — pruebas puras.
- .github/workflows/qa-automation.yml — ejecutar pruebas antes del build web.

## Riesgos y regla de aceptación

US-004 y US-011 se mantienen PARCIALES en la matriz hasta registrar capturas de navegador contra Firestore staging y comprobar métricas. Las métricas de mejora son ESTIMADAS; no cumplen el objetivo de 20% observado. Nada de estos cambios altera IAM, Firestore o Cloud Run. Se debe usar revisión web etiquetada con 0% del tráfico principal para QA.