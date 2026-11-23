# SmartRoute AI — Matriz de aceptación de historias P0 (QA)

> **ACTUALIZACIÓN 23/11/2026:** Esta matriz conserva el **baseline histórico del 22/11** (8 aceptadas/2 parciales/2 pendientes). Para el estado vigente de 12 historias P0 en QA revisar la **adenda fechada al final**: **10 aceptadas funcionalmente / 1 parcial / 1 pendiente**. No equivale a aceptación académica ni cobertura exhaustiva.

**Corte:** 22/11/2026. **Baseline:** [SPEC](../../specs/SPEC.md), sección 4: `US-001…US-011` y `US-015` son P0 (12 historias). **Prefijo US-V1** evita confundir los alias de implementación `US-IMP-011..014`. **Ruta común de evidencia:** `aec305db-6e2f-5923-8b9f-87fcd9b37755`.

**Veredicto QA conservador:** **8 aceptadas funcionalmente (66,7 %)**, **2 parciales (16,7 %)** y **2 pendientes (16,7 %)**. Este porcentaje **NO** es el cumplimiento global de rúbrica UPN, ni una tasa de cobertura exhaustiva de criterios P0. Una historia aprobada aquí significa **evidencia positiva de la función en QA**, no prueba completa de todas las restricciones, seguridad y pruebas negativas.

| US baseline P0 | Capacidad | Estado en QA | Evidencia | Pendiente o límite relevante |
| --- | --- | --- | --- | --- |
| US-V1-001 | Autenticación Google y RBAC | **Aceptado QA** | E01, E02 | Falta prueba negativa de sesión/rol ajeno |
| US-V1-002 | Panel OPERATOR | **Aceptado QA** | E01, E12 | Sin estudio formal de usabilidad |
| US-V1-003 | Crear pedido con geolocalización validada | **Aceptado QA** | E01, E03 | Falta captura aislada del POST/201 del mismo caso y validaciones negativas |
| US-V1-004 | Consultar y **filtrar** pedidos por estado | **Parcial** | E09, E12 | No se demostró filtro de pedidos por estado en operador |
| US-V1-005 | Asignar pedidos pendientes a repartidor | **Aceptado QA** | E01, E02 | Equivalencia funcional: ruta optimizada asignada; faltan pruebas de duplicidad/conductor ocupado |
| US-V1-006 | Ruta propia en Android | **Aceptado QA** | E02, E03 | Prueba negativa entre identidades pendiente |
| US-V1-007 | Actualizar estado de entrega | **Aceptado QA** | E07, E08, E09, E10 | 5 entregadas/1 fallida; motivo de fallo no auditado visualmente |
| US-V1-008 | GPS durante ACTIVE, con consentimiento | **Pendiente** | Ninguna | Coordenada de parada **no** demuestra ubicación del teléfono, consentimiento ni publicación de GPS |
| US-V1-009 | Comparar baseline vs optimizada | **Aceptado QA** | E01, E12 | Cifras *estimated*; sin ahorro observado ni optimalidad matemática certificada |
| US-V1-010 | Ver secuencia optimizada en Android | **Aceptado QA** | E03, E10, E12 | Sin navegación giro a giro, solo secuencia y mapa esquemático |
| US-V1-011 | Dashboard de KPI / puntualidad | **Parcial** | E01, E10, E12 | Distancias y tiempos estimados visibles, pero puntualidad y tiempos observados no medidos |
| US-V1-015 | Piloto comparable y exportación | **Pendiente** | E11, E12 (solo cierre QA) | Un recorrido sintético no demuestra prueba A/B, export de dataset ni impacto real |

## Criterios verificables y contrato

| Historia | Condición de aceptación demostrada / requerida | Contrato técnico actual |
| --- | --- | --- |
| US-V1-001/002 | Acceso con rol permitido; panel de operación y sesión DRIVER | Firebase + Gateway; web React y Android |
| US-V1-003/004 | Geocodificación y persistencia; listado + filtro (filtro pendiente) | `POST/GET /api/v1/orders` |
| US-V1-005 | Pedidos en ruta y conductor asignado de forma exclusiva | `POST /api/v1/optimized-routes/{id}/assign-driver` (US-IMP-011) |
| US-V1-006 | DRIVER recupera solo su ruta persistida | `GET /api/v1/driver/me/route` |
| US-V1-007 | Actualiza resultado con confirmación e idempotencia; no repetir entrega | `POST /api/v1/driver/me/route/stops/{id}/deliver|fail` (US-IMP-013) |
| US-V1-008 | GPS observado, consentimiento, timestamp, precisión y publicación | No validado |
| US-V1-009 | Misma muestra de pedidos y depósito; secuencia y estimados comparables | `POST /api/v1/optimization/preview` + OR-Tools/ORS |
| US-V1-010 | Secuencia optimizada guardada y legible en Android | `POST /api/v1/optimized-routes` + DRIVER GET |
| US-V1-011 | KPI de km, tiempo y puntualidad con origen y periodos verificables | UI comparativa parcial; puntualidad pendiente |
| US-V1-015 | Diseño experimental, muestra, dataset exportado y evaluación OE1–OE3 | No validado |

## Índice de capturas originales — respaldo del informe

Capturas **E01–E12** proporcionadas por el usuario; están incrustadas en el archivo de entrega **`SmartRoute_AI_Anexo_Matriz_Aceptacion_P0_Con_Capturas_2026-11-22.docx`**, generado aparte, y empaquetadas en `SmartRoute_AI_Evidencias_E2E_QA_2026-11-22.zip` con manifiesto SHA-256. **No se han publicado los binarios de las capturas en este repositorio**; revisar privacidad antes de compartir externamente.

| Código | Archivo original en ZIP | Evidencia |
| --- | --- | --- |
| E01 | `E01_Operador_ruta_asignada_PLANNED.png` | Operador: ruta optimizada/QA asignada, PLANNED |
| E02 | `E02_Android_ruta_6_paradas_PLANNED.png` | DRIVER: ruta asignada 6 paradas |
| E03 | `E03_Android_detalle_6_paradas.png` | Secuencia y mapa de paradas |
| E04 | `E04_Android_boton_iniciar.png` | US-IMP-012: botón inicio |
| E05 | `E05_Android_confirmacion_inicio.png` | Confirmación inicio |
| E06 | `E06_Android_parada_en_camino.png` | Parada durante ruta ACTIVE |
| E07 | `E07_Android_confirmar_entrega.png` | Confirmación entrega |
| E08 | `E08_Android_parada_entregada.png` | DELIVERED, bloqueo de repetición |
| E09 | `E09_Android_entregada_fallida.png` | 1 DELIVERED y 1 FAILED |
| E10 | `E10_Android_5_1_0_botoncierre.png` | 5 entregadas, 1 fallida, 0 pendientes |
| E11 | `E11_Android_COMPLETED.png` | Ruta completada Android |
| E12 | `E12_Operador_COMPLETED.png` | Mismo recorrido finalizado desde operador, versión 10 |

## Trazabilidad y alcance

- [SDD v2.1 (adenda as-built)](../SmartRoute_AI_Charter_SDD_v1.md), [trazabilidad](../SDD_TRACEABILITY.md), [acta de la ruta única E2E](E2E_OPERADOR_ANDROID_QA_2026-11-22.md), [matriz 36 criterios académicos](../Matriz_Maestra_Capstone_SDD.md).
- Esta **matriz de 12 historias P0** es distinta de los 36 controles académicos de la rúbrica. No se marcan automáticamente esos controles como «Validado».
- Valores mostrados: 20,96→16,8 km; 36→31 minutos redondeados; 15,84 % mejora estimada en UI. Son indicadores de matriz vial, **no** observaciones de entrega real ni prueba de OE1 ≥20 %.
- Estado `COMPLETED` confirmado en la misma ruta desde Android y lectura posterior de operador. No repetir escrituras sobre esa ruta cerrada.

## Condiciones restantes para cierre académico

1. Registrar prueba adicional de filtro web (US-004) y KPI puntualidad (US-011), o dejar explícita la brecha en el informe.
2. No declarar GPS (US-008) ni piloto/exportación (US-015) hasta pruebas reproducibles con dataset real o protocolo académico aceptado.
3. Relacionar resultados con cada control de rúbrica `EF-C13-01`, `INF-05` y `MED-02` **sin inferir aceptación formal**.
4. Revisar privacidad y adjuntar las 12 capturas del anexo en la entrega formal; CI, negativos RBAC, seguridad y costos permanecen con su propio gate.


---

## Adenda oficial — corte formal 23/11/2026 (TC-E2E-QA-20261123-02)

**Nuevo universo del corte:** exactamente las mismas **12 historias P0**. Se mantiene el historial 22/11 sin sobrescribirlo. El segundo escenario QA es la ruta **`fb413b71-c963-570f-be61-500e9eadfb7b`** de **cinco paradas**, diferente de la ruta anterior de seis. Evidencia: [acta formal 23/11](ACTA_CORTE_FORMAL_SQA_E2E_2026-11-23.md). Los códigos E23 hacen referencia a evidencias narradas y ejecutadas en la sesión del usuario; **las capturas binarias aún no están adjuntas a GitHub**.

| US baseline | Estado 23/11 | Cambios / evidencia incremental | Reserva |
| --- | --- | --- | --- |
| US-V1-001 Autenticación y RBAC | **ACEPTADA QA** | Firebase DRIVER autenticado con ruta propia; E23-01, E23-03 | Negativos de otros usuarios/roles sin ensayo desplegado |
| US-V1-002 Panel operador | **ACEPTADA QA** | Dashboard, pedidos/rutas y sedes probados en QA; evidencia anterior E12 y escenario operador nov. 2026 | Usabilidad no formal |
| US-V1-003 Crear pedido geo | **ACEPTADA QA** | Cinco pedidos sintéticos del segundo recorrido asignado | Negativos geocodificación pendientes |
| US-V1-004 Consulta/filtro de pedidos | **ACEPTADA QA** (**sube de parcial**) | En operador se contrastaron filtros 18 totales / 2 FAILED / 10 DELIVERED y reset, en sesión de preparación del segundo recorrido | Verificación de filtros y dataset con capturas sin anexos binarios en repo |
| US-V1-005 Asignación | **ACEPTADA QA** | Ruta cinco paradas asignada al QA; conductor reservado hasta cierre; E23-01, E23-12 | Negativas/concurrencia no certificadas |
| US-V1-006 Ruta propia Android | **ACEPTADA QA** | Recuperación de ruta PLANNED→ACTIVE→COMPLETED; E23-01/E23-10 | Sin ensayo negativo con otro UID |
| US-V1-007 Estado entrega | **ACEPTADA QA** | 4 DELIVERED + 1 FAILED, 0 pendientes; 2 pedidos comprobados con GET Firestore directo y 3 visualizados Android; E23-07/08/09 | Faltan 3 lecturas REST individuales y revisión del motivo persistido |
| US-V1-008 GPS ACTIVE consentido | **ACEPTADA QA** (**sube de pendiente**) | Consentimiento OS, fix del emulador recibido y persistido en Firestore HTTP 200, precisión 5 m y posterior borrado HTTP 404; E23-05/06/13 | **SIMULACIÓN**, no prueba móvil de campo, historial ni tiempo de viaje real |
| US-V1-009 Baseline vs optimizada | **ACEPTADA QA** | Ruta 5 paradas ~48,43→41,68 km, ~71→61 min; 14,59 % **estimado** | No demuestra objetivo de 20 % real |
| US-V1-010 Secuencia Android | **ACEPTADA QA** | Cinco paradas ordenadas y mapa OSM, E23-02 | Línea entre paradas no es ruta vial |
| US-V1-011 Dashboard KPI/puntualidad | **PARCIAL QA** | Distancias, tiempos y progreso se muestran; dashboard de operación disponible | Sin puntualidad observada ni datos de campo |
| US-V1-015 Piloto comparable/export | **PENDIENTE** | Segundo recorrido sintético E2E documentado, pero no equivale a muestra experimental A/B ni export de datos observado | Plan de medición, muestra, export, línea base y resultados faltantes |

**Resultado P0 funcional al 23/11:** **10/12 aceptadas = 83,33 %**, **1/12 parcial = 8,33 %**, **1/12 pendiente = 8,33 %**. Los estados se refieren exclusivamente a **capacidades funcionales observadas en QA**, con las reservas explícitas. No es avance global del producto, cumplimiento de rúbrica académica ni cobertura de pruebas.

**Trazabilidad de implementación:** US-IMP-012 (start), US-IMP-013 (deliver/fail), US-IMP-014 (complete) fueron probadas y se vinculan con US-V1-006/007/008; no renumerar ni sustituir los identificadores del baseline.

**SQA:** resultado de cierre REST independiente 5/5 en ruta `fb413b71-...`: status COMPLETED, conductor disponible, reserva borrada, historial presente, GPS eliminado. La persistencia de GPS se verificó **antes** del cierre (HTTP 200). No reutilizar ruta cerrada. No presentar datos simulados como observaciones reales.

**Siguiente gate:** adjuntar screenshots originales con autorización/anonimización; export de logs, controles negativos y requisitos éticos/seguridad; piloto comparable. Mantener la fecha de ambos escenarios, evitando mezclar el 22/11 de seis paradas con el 23/11 de cinco.
