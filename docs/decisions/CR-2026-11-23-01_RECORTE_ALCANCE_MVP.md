# CR-2026-11-23-01 — Reducción de alcance del MVP SmartRoute AI

**Fecha:** 2026-11-23 · **Decisión del responsable del proyecto:** simplificar el MVP tras contrastar prototipos y software ejecutable. **Tipo:** control de cambios SDD, solo documentación; sin borrar código ni evidencias anteriores.

## 1. Decisiones aprobadas

| Elemento | Decisión | Efecto en desarrollo / UX |
| --- | --- | --- |
| Deshacer una entrega durante seis segundos (ADR-09, Fig. 14) | **EXCLUIDO** | Mantener confirmación explícita actual antes de registrar entrega; no implementar rollback temporal. Conservar seguridad, idempotencia y auditoría |
| Semáforo visual de puntualidad «a tiempo / en riesgo / retrasado» (Fig. 18) | **EXCLUIDO** | No desarrollar etiquetas de colores ni reglas de umbral 15 minutos. Se pueden mantener tiempos estimados, estado de entrega e indicadores cuantitativos de tiempo/distancia sin semáforo |
| Modo sin conexión y cola local con reenvío (US-013/014, Fig. 15) | **EXCLUIDO** | No implementar almacenamiento local offline ni sincronización diferida; la aplicación requiere conexión para registrar estados, muestra error claro sin confirmación falsa y reintenta únicamente de forma segura conforme a la idempotencia existente |
| Funcionalidad de exportación de resultados/dataset (componente de US-015) | **EXCLUIDO** | No construir botón ni endpoints CSV/JSON de exportación del piloto como funcionalidad del producto. Conservar la documentación y evidencia técnica normal del proyecto sin convertirla en funcionalidad de exportación |

**Distinción fundamental:** retirar exportación **no equivale a retirar el piloto**. Se mantiene una validación experimental/comparativa usando datos verificables de pruebas y métricas, con evidencia documentada por medios de QA/consultas controladas. No se afirmará reducción real sin datos observados comparables y método explícito.

## 2. Alcance restante

- **US-011**: panel de indicadores centrado en tiempo base vs optimizado, distancia, efectividad y origen `estimated/observed`. Eliminar semáforo de riesgo. Una métrica cuantitativa de puntualidad debe revisarse contra los objetivos del informe; la decisión actual elimina específicamente **el semáforo**, no revoca sin más la investigación ni la medición temporal.
- **US-016**: seguimiento de pedido simplificado con estado e historial, ETA o ventana estimada cuando haya datos suficientes y, si se mantiene, enlace público seguro; **sin semáforo**.
- **US-015**: separar formalmente `US-015-PILOTO` (validación metodológica/comparativa, evidencia y evaluación) de `US-015-EXPORT` (**excluida**). La capacidad de guardar pruebas y el control de calidad permanecen.
- **US-012** Gemini consultivo continúa como historia P1 hasta decisión posterior.
- **SEC-01** y **DEF-01** continúan como controles de calidad; no se reabren rutas QA COMPLETED ni se redistribuye tráfico en GCP.

## 3. Impacto documental y de medición

El informe y las presentaciones entregadas **22/11/2026** describen el alcance anterior. **No reescribir la entrega histórica como si esta decisión hubiera existido entonces.** Emitir adenda de alcance con fecha 23/11 para las versiones siguientes, revisar: Project Charter, SPEC, SDD, ADR-09 y ADR-11, RF/AC, backlog, matriz de trazabilidad, plan de QA, prototipos (figuras 14, 15 y 18), cronograma, evidencia, métricas y diapositivas.

- **No reportar 100 % ni conservar automáticamente el avance 63,7 % como avance del nuevo alcance.** La cifra 45,2/71 = 63,7 % permanece **histórica** y corresponde al universo anterior.
- US-013/014 sumaban **8 puntos** y ahora se excluyen por completo; esto llevaría el denominador a **63** *antes de revisar US-015*.
- US-015 sumaba **5 puntos** conjuntamente por exportación **y** piloto; al conservar piloto, **no se pueden descontar los cinco puntos sin dividir/reestimar la historia**. El nuevo denominador y porcentaje son **pendientes de reestimación explícita**.
- Deshacer y semáforo eran detalles de UX/requisitos, no historias independientes con puntos propios: evitar restar puntos arbitrarios sin revisar criterios de aceptación.

## 4. Criterios de aceptación revisados

1. Android confirma la entrega antes de enviarla; no promete deshacer.
2. La pérdida de red no muestra un pedido entregado sin confirmación del servidor; mensaje de error claro, sin cola offline.
3. Panel de KPI y seguimiento presentan estados y tiempos con distinción estimado/observado, sin semáforo.
4. El MVP no ofrece exportación de resultados como característica funcional.
5. Piloto mantiene protocolo, límites, muestras y resultados verificables para cumplir el Capstone, aunque no exista herramienta de exportación.

**Estado del cambio:** decisión de alcance registrada. **Pendiente:** reconciliar los archivos de especificación y la matriz de puntos en un PR SDD específico antes de asignar nuevas cifras oficiales.
