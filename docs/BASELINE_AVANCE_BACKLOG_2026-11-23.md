# SmartRoute AI — Línea base de avance, reconciliación y secuencia de ingeniería
**Corte:** 23/11/2026 (America/Lima) · **Carácter:** auditoría de métricas y backlog; no modifica código ni datos del piloto.

## 1. Tres indicadores diferentes — no sustituibles

| Indicador | Universo | Cálculo / fuente | Valor y estado |
| --- | --- | --- | --- |
| Historias P0 con evidencia de aceptación QA | 12 historias inmutables US-V1-001…011, 015 | 10 aceptadas / 12; [matriz E2E P0](evidence/MATRIZ_ACEPTACION_P0_2026-11-22.md) | **83,33 % verificado**; 1 parcial y 1 pendiente. Criterio funcional, no score académico |
| Avance P0 ponderado al 23/11 | Historia con peso y % parcial | Informe académico del 22/11, tabla 87: **44,2/58 (76,2 %)**. GPS US-008 suma 1 punto adicional según nuevo E2E QA (75→100 %), por lo que **45,2/58 = 77,93 %** | **RECONCILIADO ARITMÉTICAMENTE**, avance de GPS condicionado a aceptación QA emulador; dispositivo físico sigue pendiente |
| Avance funcional global ponderado al 23/11 | **71 puntos** (P0 + P1 y US-016 extendida) | Informe académico entregado 22/11: **44,2/71 = 62,25 %**; GPS pasó de 3/4 puntos a 4/4 por nueva prueba QA: **45,2/71 = 63,66 %** | **RECONCILIADO** con tabla 87 del informe, sujeto al alcance QA emulado de US-008 |
| Requisitos académicos UPN | 36 controles | [Matriz maestra](Matriz_Maestra_Capstone_SDD.md), [CSV](Matriz_Capstone_SmartRoute_v1.csv) | No calcular avance global por extrapolación de historias QA |
| Resultado del recorrido de 5 paradas | 5 paradas resueltas | 4 DELIVERED + 1 FAILED = 5 | **100 % resolución**, **80 % entregas exitosas**, exclusivamente QA simulado |
| Beneficio de optimización | Comparación vial estimada de una ruta | 48,43 km / 71 min versus 41,68 km / 61 min; cifra reportada 14,59 % | Solo **estimado**; DEF-01 debe precisar si denominador mide km, tiempo o cálculo interno y la fuente exacta |

**Regla de cálculo reproducible** para el indicador ponderado: 
`progress_weighted = SUM(weight_i * completion_fraction_i) / SUM(weight_i)`, con `completion_fraction_i` entre 0 y 1, fecha, política de redondeo, evidencia, dueño y versión de cada fila. **No inventar** pesos o fracciones para reproducir el valor reportado.

**Hallazgo R-01 (resuelto documentalmente):** la [SPEC](../specs/SPEC.md), §4, define P0 US-001…011 y US-015; P1 US-012…014. El **informe académico entregado el 22/11**, tabla 87, usa una **línea base extendida** con **US-016 de seguimiento = 5 puntos** y total 71, de los cuales 58 P0. US-017 catálogo de sedes es extra y no suma. La SPEC aún no está reconciliada con la ampliación: registrar la discrepancia y preservar ambos denominadores, sin confundirlos.

**Hallazgo R-02:** los alias US-IMP-011…014 corresponden a implementar asignación/inicio/entrega/cierre. No confundir con US-V1-011 (KPI), US-V1-012 (Gemini), US-V1-013/014 (incidencias/offline).

**Hallazgo R-03:** el informe académico tabla 91 respalda **176 tests aprobados** al 22/11 (API 97+11 del emulador, Gateway 29, web 8, Android 42; hay que distinguir tests ejecutados en CI de omitidos localmente). El reporte del 23/11 cita **179**, incremento de tres Android, pero debe contrastarse con los reportes de GitHub Actions del PR #73 y contabilización por suite antes de certificar el total.

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

**Conclusión profesional:** el **63,7 %** y **77,9 %** quedan aritméticamente reconciliados con la **tabla 87 del informe presentado el 22/11 y un punto adicional por GPS QA**. Requieren distinguir *100 % cumplimiento US-008 en QA simulado* de validación en teléfono físico. El **83,33 %** corresponde al conteo de historias aceptadas funcionalmente en QA de la matriz del repositorio; **no es ponderación**. Ninguno certifica producción o rúbrica.


---

## 5. Comparación del Anexo 04 del informe presentado el 22/11 vs UI implementada (23/11)

**Documento fuente académico:** `2026-2_ISC-Informe_Proyecto Final_CAPST_Grupo 2.docx`, **Anexo 04 (páginas impresas 93–97), Figuras 14–20**, tabla 87 (pág. 65) y compromiso de cierre tabla 88 (pág. 66). **Evidencia de implementación:** código de `apps/operator-web/src/main.jsx`, `RouteDetailScreen.kt`, `StopDetailScreen.kt`, acta E2E y capturas de Android 23/11.

**Advertencia:** los prototipos HTML son especificación UX con datos sintéticos **sin conexión Backend**; no deben darse por implementados al aparecer en el informe o una presentación. El informe menciona `docs/prototype/index.html` y PR #52, pero **ese HTML no aparece en el árbol `main` consultado al corte**; se contrastaron las figuras del documento y los archivos de aplicación versionados, no una ejecución actual del prototipo.

| Figura / flujo del prototipo | Diseño presentado | Implementación efectivamente validada | Brecha de desarrollo |
| --- | --- | --- | --- |
| Fig. 14 bienvenida, consentimiento, Mi ruta y entrega con deshacer 6 s | UI oscura/amarilla, consentimiento explicado, barra/progreso por ruta, entrega con deshacer | Login Google, ruta propia, permiso GPS, progreso, entrega y cierre **PASS QA**; Android usa interfaz Compose distinta. `StopDetailScreen.kt` confirma **acción irreversible** «no se puede deshacer» | **UX/paridad pendiente**: deshacer 6 s no implementado; consentimiento previo ilustrado y estilo/microinteracciones no equivalentes |
| Fig. 15 entrega fallida/offline/privacidad | Motivos clasificados, comentario, cola sin señal, pantalla Cuenta con revocar GPS | Motivo obligatorio y FAILED **PASS**; GPS permitido durante ACTIVE; no existe flujo offline ni cola recuperable en pantallas implementadas | **US-V1-013/014 pendiente**, revocación/cuenta y clasificación de motivo a evaluar por alcance |
| Fig. 16 Operador: ruta y baseline vs optimizada | Vista comparativa con mapa, secuencia, diferencias | Operador React tiene optimización ORS+OR-Tools, pedidos, rutas, mapa, KPI estimados y asignación **PASS QA** | Diferencias de layout/estilo; DEF-01 conciliar % y redondeo; no confundir geometría de mapa con distancia vial |
| Fig. 17 seguimiento repartidor/destinatario | Timeline, compartir enlace, ETA en rango sin ubicación del conductor, enlace vencido | No hay pantalla de timeline, compartir enlace o página pública de destinatario en web/Android `main` | **US-016 pendiente (5 puntos)**; proteger token público y evitar exponer ubicaciones (SEC-07) |
| Fig. 18 seguimiento operador | Tabla por pedido con ETA, ventana, semáforo a tiempo/en riesgo/retrasado | Panel de operador muestra listados, estados y KPI de eficiencia, pero no módulo seguimiento con semáforo/ETA | **US-016 pendiente**, dependencia de US-011 y datos suficientes para ETA; debe diferenciar `estimated` de `observed` |
| Fig. 19 búsqueda de direcciones/ruta inviable | Autocomplete y aviso 422 ante ruta inviable | API tiene autocomplete en Gateway y validación de matriz; UI operador usa creación de pedidos/geocodificación; rutas optimizadas probadas | **Paridad visual parcial**: verificar experiencia y manejo visible de 422 en UI, no declararlo terminado por contrato |
| Fig. 20 Gemini consultivo | Chat con respuestas fundamentadas, muestra de payload sin PII, protección prompt injection | No existe vista de Gemini en `main.jsx`; no probado en E2E | **US-012 P1, 5 puntos pendientes** y golden eval set de 20 casos; no sobreprometer |
| Fig. 21 anotaciones Nielsen/OWASP | Heurísticas de usabilidad y seguridad en prototipo | Acta SQA y controles de código existen | Evaluación heurística y usabilidad formal en Android/web **pendientes** |

### Consecuencias en alcance, no solo estética

- **Faltan flujos completos, no solo retoques:** seguimiento destinatario/repartidor/operador (US-016), modo sin conexión (US-013/014), asistente Gemini (US-012) y medición/exportación P0 (US-011/015).
- **Inconsistencia explícita de UX:** prototipo promete deshacer entrega durante 6 s; Android muestra operación irreversible. La resolución requiere una decisión de requisito/ADR y semántica de backend, **no simplemente pintar un botón**.
- **El diseño de tracking público añade superficie de ataque:** SEC-07 debe contemplar tokens no enumerables, expiración, `Cache-Control`, `noindex`, rate limit, RBAC y privacidad.
- **Falta paridad de look-and-feel:** prototipo navy/amarillo, sidebar de operador y tarjetas de conductor contrastan con interfaz funcional actual. Clasificar como deuda UX sin confundirla con cumplimiento E2E.
- **El backlog visual se revisará antes de SEC-01/DEF-01**, pero el orden de implementación acordado permanece SEC-01 → DEF-01 → US-011 → US-016 → US-015, sujeto a evidencias/alcance.
