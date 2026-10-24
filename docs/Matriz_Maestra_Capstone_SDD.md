# Matriz maestra Capstone ↔ SmartRoute AI (v1.0)

**Estado:** planificación y especificación; ningún criterio se marca como cumplido sin evidencia. **Fuentes primarias:** `2026-2_ISC-Informe_Proyecto Final_CAPST.docx`, `T1_Informe_Medicion_CAPST.docx` y `EF_Informe_Medicion_CAPST.docx` (UPN 2026-2). La matriz es una transcripción operativa/síntesis de criterios, no sustituye las plantillas originales.

## Uso y reglas

1. Usar el [CSV editable](Matriz_Capstone_SmartRoute_v1.csv) como registro oficial de seguimiento (estado inicial `Pendiente`, responsable `Por asignar`).
2. Completar `ruta_evidencia` con un vínculo estable en repositorio, informe, prueba o acta; asignar responsable.
3. Cambiar a `Validado` solo después de verificar el umbral, la evidencia y su consistencia con los objetivos. Estados permitidos: `Pendiente`, `En curso`, `En revisión`, `Validado`, `Bloqueado`.
4. No inventar evidencias, porcentajes, muestras, fuentes bibliográficas ni mejoras; marcar explícitamente pruebas simuladas y resultados reales.
5. `MED-xx` representa decisiones de medición propuestas para SmartRoute, no exigencias literales nuevas de la UPN.

## Matriz de cumplimiento (36 controles)

| ID | Competencia/Origen | Sección UPN | Criterio y umbral | Evidencia planificada | Semana | Estado |
|---|---|---|---|---|---|---|
| T1-C11-01 | T1 C1.1 | III 3.1–3.2 | Problema sustentado con al menos 5 evidencias objetivas | Registro de fuentes, entrevistas, observaciones y datos fechados | S1 | Pendiente |
| T1-C11-02 | T1 C1.1 | III 3.2 | Más de 3 causas raíz y más de 3 efectos, actores y restricciones | Pareto, Ishikawa y 5 porqués con resultados y causas | S1 | Pendiente |
| T1-C11-03 | T1 C1.1 | III 3.2 | Aplicar por lo menos 3 técnicas de análisis causal | 3 análisis documentados con evidencia contrastable | S1 | Pendiente |
| T1-C11-04 | T1 C1.1 | III 3.3, 3.5–3.10 | Variables, población, muestra, dimensiones, indicadores e instrumentos | Operacionalización, muestreo e instrumento con validez y confiabilidad | S1–S2 | Pendiente |
| T1-C12-01 | T1 C1.2 | V 5.1 | Evaluar al menos 3 alternativas viables | Matriz de alternativas: proceso manual mejorado, SaaS, SmartRoute AI; validar selección | S2 | Pendiente |
| T1-C12-02 | T1 C1.2 | V 5.1 | Matriz ponderada con 5 o más criterios medibles | Pesos total 100 %, escala 1–5, cálculo y fuentes de puntuación | S2 | Pendiente |
| T1-C12-03 | T1 C1.2 | IV, V 5.5 | Justificación fidedigna, restricciones, recursos y arquitectura | Informe de trade-offs y selección justificada | S2 | Pendiente |
| T1-C21-01 | T1 C2.1 | II 2.1, V 5.2 | Identificar usuarios, cliente, proceso y organización | Ficha del contexto y patrocinador real o supuesto explícito | S1 | Pendiente |
| T1-C21-02 | T1 C2.1 | V 5.2 | Al menos 4 necesidades sustentadas con mínimo 3 evidencias | Matriz NEC-01…04 con fuente rastreable | S1 | Pendiente |
| T1-C21-03 | T1 C2.1 | V 5.2 | Al menos 6 restricciones de diseño realistas | Registro de restricciones con su impacto | S2 | Pendiente |
| T1-C21-04 | T1 C2.1 | V 5.2, 5.6, 5.9 | 4 o más requisitos o historias trazables | Vínculo NEC→OBJ→US→diseño→prueba | S2 | Pendiente |
| EF-C13-01 | EF C1.3 | VI 6.1–6.3 | Solución funcional con al menos 90 % de requisitos priorizados | Demo + porcentaje calculado sobre backlog P0 congelado | S3–S7 | Pendiente |
| EF-C13-02 | EF C1.3 | V 5.6, VI, VII 7.6 | Trazabilidad integral problema→resultado | Matriz actualizada con implementación y resultados reales | S2–S7 | Pendiente |
| EF-C13-03 | EF C1.3 | VI 6.2–6.4, VII 7.3 | Métricas de rendimiento, calidad o valor | Logs, reportes de pruebas y mediciones contrastables | S5–S7 | Pendiente |
| EF-C22-01 | EF C2.2 | IV, V 5.5 | Justificar al menos 5 decisiones de diseño | 5 fichas ADR sobre stack, despliegue, datos, optimizador, seguridad | S2 | Pendiente |
| EF-C22-02 | EF C2.2 | V 5.5 | Al menos 5 artefactos técnicos de ingeniería | Arquitectura C4, BPMN, ERD, OpenAPI, prototipos, plan de pruebas | S2–S5 | Pendiente |
| EF-C22-03 | EF C2.2 | IV, V 5.1, VI | Evaluar 3 alternativas y considerar 4 principios de ingeniería | Matriz decisiones + modularidad, mínimo privilegio, trazabilidad, privacidad por diseño | S2 | Pendiente |
| EF-C23-01 | EF C2.3 | V 5.2, VII 7.3 | Al menos 90 % de necesidades específicas satisfechas | Necesidades iniciales con pruebas y criterio objetivo por necesidad | S7 | Pendiente |
| EF-C23-02 | EF C2.3 | VII 7.3 | Al menos 3 indicadores asociados a necesidades, requisitos y objetivos | Tiempo por entrega, km/ruta, puntualidad; antes/después comparable | S1,S7 | Pendiente |
| EF-C23-03 | EF C2.3 | V 5.3, 5.8, VII–VIII | 6 factores de contexto, 3 riesgos, 3 limitaciones, 3 efectos no deseados, 3 mejoras | Matriz de impactos y acciones sustentadas en resultados | S2,S7 | Pendiente |
| EF-C41-01 | EF C4.1 | IX 9.1 | 5 responsabilidades, 5 riesgos éticos, 5 controles verificables | Matriz ética con pruebas de controles y consecuencias | S2–S7 | Pendiente |
| EF-C41-02 | EF C4.1 | V 5.11, IX 9.2–9.4 | Privacidad, seguridad y compromiso ético individual; uso responsable de IA | Controles GPS, consentimiento, roles, retención, prompts declarados | S2–S7 | Pendiente |
| EF-C42-01 | EF C4.2 | V 5.3, 5.4, VII 7.4 | Al menos 6 factores de impacto y 3 impactos negativos con mitigación | Matriz social/cultural/económico/político/legal/ambiental/seguridad | S2,S7 | Pendiente |
| EF-C43-01 | EF C4.3 | VII 7.5, VIII 8.1–8.2 | Veredicto implementar / implementar con mejoras / no implementar | Decisión argumentada con 3 criterios técnicos/éticos/profesionales | S7 | Pendiente |
| INF-01 | Informe | I–II | Resumen, abstract, motivación, hallazgos y 5 palabras clave | Redacción con resultados reales y traducción | S1,S7 | Pendiente |
| INF-02 | Informe | III 3.1 | Mínimo 5 antecedentes de antigüedad máxima 5 años | Revisión de antecedentes y referencias APA 7 | S1 | Pendiente |
| INF-03 | Informe | V 5.6–5.10 | Business Case, EDT/cronograma, gestión de riesgos, interesados y presupuesto | VAN/TIR si corresponde, matrices, cálculos y supuestos | S2–S7 | Pendiente |
| INF-04 | Informe | V 5.11–5.12 | Plan de seguridad en BD, aplicación e infraestructura y SQA ISO/IEC 25010 | Modelo de amenazas, controles y estrategia de pruebas | S2–S6 | Pendiente |
| INF-05 | Informe | VI 6.2–6.3 | Pruebas unitarias y aceptación, evidencia de despliegue y uso | Reportes con cantidad de pruebas, funciones y capturas/URLs | S3–S7 | Pendiente |
| INF-06 | Informe | VII 7.6–VIII | Resultados por 3 objetivos específicos, general y conclusiones correspondientes | Tabla objetivo→indicador→resultado→conclusión; validación usuarios | S7 | Pendiente |
| INF-07 | Informe | XI y notas p.16–17 | Producto implementado, video máximo 10 min (3 teoría,7 producto) | Enlace vídeo OneDrive institucional; código/documentación en OneDrive | S7 | Pendiente |
| INF-08 | Informe | Notas p.16 | Informe Arial 12, A4, 1.5, justificado, APA 7 | Revisión editorial y de formato | S7 | Pendiente |
| INF-09 | Informe | IX 9.2–9.4 | Declaración ética personal de cada integrante y registro de prompts IA | Secciones individuales y bitácora de IA | S1–S7 | Pendiente |
| INF-10 | Informe | V 5.3.8 | Comparar impactos de soluciones en contextos | Matriz comparativa de impactos | S2 | Pendiente |
| MED-01 | Diseño SmartRoute (propuesta) | III 3.4, VII 7.3 | Hipótesis de reducción de tiempo de entrega 20 % | Definición operativa y mismo tipo de rutas en línea base y piloto | S1,S7 | Pendiente |
| MED-02 | Diseño SmartRoute (propuesta) | VI 6.4, VII 7.3 | Distinguir métricas observadas de estimaciones/simulaciones | Dataset con campo origen; análisis sin presentar simulación como piloto real | S1–S7 | Pendiente |

## Cadena SDD de trazabilidad

`EVIDENCIA_PROBLEMA → CAUSA_RAÍZ → NECESIDAD (NEC) → OBJETIVO (OBJ) → REQUISITO/HISTORIA (US/RF) → ARTEFACTO (ADR/API/ERD/UX) → IMPLEMENTACIÓN → PRUEBA (TC) → KPI/RESULTADO → RE1/RE2/RE4`.

Cada historia P0 debe enlazar al menos una necesidad y una prueba; cada resultado debe anotar muestra, origen (real/simulado), fecha, fórmula y condiciones del piloto. Calcular **cobertura P0 = requisitos P0 validados / total P0 priorizados**, y **satisfacción necesidades = necesidades con aceptación demostrada / necesidades específicas definidas**. Ambas metas de rúbrica son >= 90 % y son independientes.

## Indicadores iniciales para SmartRoute (propuestos, sin datos aún)

| Indicador | Fórmula | Línea base | Meta | Fuente |
|---|---|---|---|---|
| Tiempo promedio por entrega | Suma de minutos observados / entregas comparables | Por medir | -20 % | registro de operación/piloto |
| Distancia por ruta | Suma de km registrados por ruta | Por medir | Determinar en diagnóstico | GPS / proveedor de mapas |
| Puntualidad | Entregas dentro de la ventana / entregas medidas ×100 | Por medir | Determinar en diagnóstico | marcas de tiempo |

**Advertencia metodológica:** la reducción estimada de tiempos de Google Maps no equivale a una mejora real de entrega. Nunca combinar datos reales y simulados sin etiqueta y análisis separado.

## Gaps importantes detectados

- El caso ficticio y los datos sintéticos no bastan por sí solos para sustentar el criterio T1 de problema **real** con cinco evidencias objetivas. Requiere datos de una operación real o acuerdo académico explícito de validez del caso simulado.
- Se deben validar población, muestra, instrumentos, cinco antecedentes recientes, tres análisis causales y tres alternativas antes de cerrar la fase de diseño.
- La plantilla de informe y la rúbrica T1 presentan algunas referencias de numeración diferentes (por ejemplo Business Case e interesados). Para el informe final, seguir la numeración de la plantilla y conservar la referencia al criterio de rúbrica en esta matriz.
- La plantilla menciona resultados de visita a cachimbos y validación de usuarios: confirmar su alcance práctico con el docente y documentar su ejecución si se exige.
- El plazo de siete semanas proviene de la propuesta 7 seleccionada; las plantillas del informe no prueban por sí solas que el cronograma académico cubra exactamente siete semanas.

## Estructura sugerida de evidencias

`evidence/t1/` diagnóstico y selección; `evidence/design/` ADR, ERD, OpenAPI, prototipos; `evidence/tests/` automatizadas y aceptación; `evidence/pilot/` datos y KPI; `evidence/ethics/` matriz y pruebas de control; `evidence/final/` enlaces oficiales e informe.
