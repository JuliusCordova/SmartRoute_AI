# SmartRoute AI — Línea base de avance, reconciliación y secuencia de ingeniería
**Corte:** 23/11/2026 (America/Lima) · **Carácter:** auditoría de métricas y backlog; no modifica código ni datos del piloto.

## 1. Tres indicadores diferentes — no sustituibles

| Indicador | Universo | Cálculo / fuente | Valor y estado |
| --- | --- | --- | --- |
| Historias P0 con evidencia de aceptación QA | 12 historias inmutables US-V1-001…011, 015 | 10 aceptadas / 12; [matriz E2E P0](evidence/MATRIZ_ACEPTACION_P0_2026-11-22.md) | **83,33 % verificado**; 1 parcial y 1 pendiente. Criterio funcional, no score académico |
| Avance P0 ponderado declarado externamente | Historia + porcentaje de completitud específico + pesos | Informe externo reporta **77,9 %**, pero no se aportó hoja reproducible de pesos, redondeos y evidencia que lo sustente | **REPORTADO, NO AUDITADO** |
| Avance funcional global ponderado declarado externamente | **71 puntos** de historias y pruebas, incluida P1 | Informe externo: **45,2 / 71 = 63,66 %**, redondeado **63,7 %**; previo 62,3 % | **REPORTADO, NO AUDITADO**. Falta matriz de 71 puntos con evidencias |
| Requisitos académicos UPN | 36 controles | [Matriz maestra](Matriz_Maestra_Capstone_SDD.md), [CSV](Matriz_Capstone_SmartRoute_v1.csv) | No calcular avance global por extrapolación de historias QA |
| Resultado del recorrido de 5 paradas | 5 paradas resueltas | 4 DELIVERED + 1 FAILED = 5 | **100 % resolución**, **80 % entregas exitosas**, exclusivamente QA simulado |
| Beneficio de optimización | Comparación vial estimada de una ruta | 48,43 km / 71 min versus 41,68 km / 61 min; cifra reportada 14,59 % | Solo **estimado**; DEF-01 debe precisar si denominador mide km, tiempo o cálculo interno y la fuente exacta |

**Regla de cálculo reproducible** para el indicador ponderado: 
`progress_weighted = SUM(weight_i * completion_fraction_i) / SUM(weight_i)`, con `completion_fraction_i` entre 0 y 1, fecha, política de redondeo, evidencia, dueño y versión de cada fila. **No inventar** pesos o fracciones para reproducir el valor reportado.

**Hallazgo R-01:** la [SPEC](../specs/SPEC.md), §4, define P0 **US-001…011 y US-015**; P1 **US-012…014**. Un informe externo menciona **US-016** y nuevas agrupaciones de historias. Debe comprobarse si pertenecen a un backlog extendido; el repositorio tiene endpoints de seguimiento del conductor y referencia a US-017 de sedes. **No añadir US-016 al denominador de la especificación baseline sin una decisión de control de cambios.**

**Hallazgo R-02:** los alias US-IMP-011…014 corresponden a implementar asignación/inicio/entrega/cierre. No confundir con US-V1-011 (KPI), US-V1-012 (Gemini), US-V1-013/014 (incidencias/offline).

**Hallazgo R-03:** el reporte externo cita 179 tests PASS. Aún falta un manifiesto que identifique **run ID, commit, jobs, test totals y skipped** para reproducir exactamente ese conteo; CI verde por sí solo no certifica el número.

## 2. Backlog ordenado acordado y sus gates

| Secuencia | Referencia | Trabajo | Criterio de finalización verificable |
| --- | --- | --- | --- |
| 0 | RECON-01 | Conciliar 71 puntos y denominadores; fijar métricas QA y académicas, sin inflar porcentaje | Esta línea base publicable; pendiente sólo **fuente externa de pesos** |
| 1 | SEC-01 | Revocación de Firebase ID tokens en Gateway y API, tolerancia a fallas, pruebas adversariales | Tokens revocados reciben 401; token válido se procesa; errores de verificación no abren acceso; CI y QA verdes |
| 2 | DEF-01 | Reconciliar definición de mejora (%) y valores exactos del motor/UI | % procede de un único cálculo documentado, mismo KPI/base y redondeo coherente; tests de regresión |
| 3 | US-V1-011 | Dashboard de puntualidad/medición y fuente de KPI | KPI distinguibles estimated/observed; sin puntualidad inventada; tests |
| 4 | US-016 (pendiente de mapeo) | Seguimiento de pedido / vista operador y estado | Contrato, historia, UI y pruebas de propietario definidos tras validar alcance |
| 5 | US-V1-015 | Export piloto y trazabilidad de dataset | CSV/JSON con origen, registros y datos completos, protocolo comparable y pruebas; no alegar mejora real sin muestra observada |

**Nota de alcance:** Gemini US-V1-012 y offline US-V1-013/014 permanecen P1 y se tratarán después de completar P0 y los gates de seguridad; un backlog extendido de 71 puntos debe aprobarse antes de incorporarlo al plan congelado.

## 3. Reglas para ejecutar esta secuencia

1. Un PR por gate, tests y evidencias asociadas; no mezclar cambios de seguridad, algoritmo, presentación y exportación en un solo merge.
2. Mantener API y Gateway Cloud Run QA etiquetados; **sin desplegar ni cambiar tráfico, IAM, base Firestore o credenciales como parte de esta documentación**.
3. No reabrir rutas QA COMPLETED `fb413b71-...` y `aec305db-...`.
4. La coordenada GPS de emulador se guardó como `observed`: requiere trazabilidad segura por ambiente/dispositivo (no confiar en etiqueta libre del cliente). Registrar defecto **GPS-ORIGIN-01** separado de SEC-01/DEF-01.
5. La matriz de 36 controles UPN requiere evaluación autónoma; el 83,33 % P0 de QA **no** significa que se haya superado umbral académico de 90 %.
6. Después de cada merge, actualizar estado y evidencia con SHA, URL de PR, pruebas ejecutadas; no declarar el trabajo posterior terminado por anticipado.

## 4. Referencias

- [Acta formal SQA E2E (23/11)](evidence/ACTA_CORTE_FORMAL_SQA_E2E_2026-11-23.md)
- [Matriz P0 QA con adenda 23/11](evidence/MATRIZ_ACEPTACION_P0_2026-11-22.md)
- [Trazabilidad SDD](SDD_TRACEABILITY.md)
- [Backlog original de siete semanas](../specs/BACKLOG_7_WEEKS.md)
- [SPEC baseline](../specs/SPEC.md)

**Conclusión profesional:** el 63,7 % ponderado es una cifra **comunicada**, no aún un cálculo independiente reproducible; el 83,33 % es una tasa **QA de historias aceptadas**, y ninguno certifica producción o aceptación de la rúbrica.
