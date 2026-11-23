# SmartRoute AI — Estado del Capstone al 22/11/2026

> **NOTA DE VIGENCIA (23/11/2026):** el contenido siguiente es el **corte histórico del 22/11** para la primera ruta de 6 paradas y no debe leerse como el último estado del proyecto. Ver la **adenda formal del 23/11 al final** y la [acta SQA E2E](evidence/ACTA_CORTE_FORMAL_SQA_E2E_2026-11-23.md). La matriz P0 vigente es **10 aceptadas/1 parcial/1 pendiente en QA**; estas cifras no acreditan la rúbrica UPN ni un piloto real.

**Veredicto:** MVP académico funcional en **QA** con flujo operativo de seis pedidos y cierre E2E demostrado; **no** se declara producción ni cumplimiento de la meta del 20 %. [Evidencia](evidence/E2E_OPERADOR_ANDROID_QA_2026-11-22.md).

## Estado por capacidad

| Módulo | Estado | Evidencia / alcance |
| --- | --- | --- |
| SDD, contratos, arquitectura y ADR | Implementado en repo; requiere actualización de matriz académica | `specs/`, `docs/`, ADR-16 |
| OPERATOR web (React) | E2E QA validado | Pedidos sintéticos, optimización, persistencia, asignación y lectura final |
| Optimización OR-Tools + ORS | Funcional con matriz vial estimada | Comparación 20,96→16,8 km; 36→31 min mostrados; mejora mostrada 15,84 % |
| Firebase Auth y roles | Validado funcionalmente en QA | Login OPERATOR/DRIVER y acceso por Gateway |
| Gateway privado → Backend | Validado en QA tras corrección allowlist | `qa-gateway-v3` → `qa-route-v2`; IAM `run.invoker` existente |
| Firestore `smartroute` | Evidencia de lectura final desde otra aplicación | Ruta QA COMPLETED v10, 5 DELIVERED y 1 FAILED visibles |
| Android Kotlin/Compose | Funcional en DEBUG QA | US-011/012/013/014; mapas OSM; no iOS |
| Seguridad para distribución | **Pendiente** | El build local habilitó `ENABLE_QA_WRITE_TEST=true` con UID/ruta fija; en `main` debe seguir false |
| CI/CD y smoke | QA automatizada disponible; último gate de este cambio por revisar | `.github/workflows/qa-automation.yml`; build manual QA v3; no inferir release a producción |
| KPIs con datos reales | **Pendiente** | Ningún tiempo GPS/entrega real recogido ni estudio A/B comparable |
| Gemini consultivo | No validado en flujo E2E | Diseño previsto / backlog, no declarar implementado |
| Video, informe final, capturas embebidas | **Pendiente** | Capturas en conversación, aún no versionadas en repositorio |

## Próximos pasos prioritarios

1. **P0 — Evidencia académica:** archivar capturas E2E con nombres y fechas, enlazar CI validado, actualizar matriz de trazabilidad y presentación/informe con Android nativo y OSM/ORS, sin confundir estimaciones con observaciones.
2. **P0 — Endurecimiento:** eliminar UID/ruta fijos del camino de distribución, hacer que la autorización por conductor y ruta dependa del Backend/roles, y negar mutaciones QA por defecto; ejecutar pruebas negativas y de regresión.
3. **P0 — Reproducibilidad:** construir y desplegar desde imagen inmutable y pipeline versionado, verificar 0 % traffic tags y rollback; no apuntar Android productivo a etiquetas de pruebas.
4. **P1 — Observabilidad:** exportar resultados de Firestore/Cloud Logging para la ejecución E2E y añadir correlación de solicitudes sin registrar tokens/datos sensibles.
5. **P1 — Medición:** piloto comparable con tiempos de entrega reales, km realmente recorridos, puntualidad y tamaño de muestra justificado; evaluar objetivo del 20 %.
6. **P2 — Extensiones:** Gemini consultivo con guardrails, ETA predictivo cuando existan datos, GPS/navegación real e iOS si el alcance futuro lo requiere.

## Criterio de finalización

**Cerrado:** el flujo funcional de la ruta QA `aec305db-6e2f-5923-8b9f-87fcd9b37755` en Android y panel web. **Abierto:** endurecimiento de seguridad, pruebas automatizadas de ese escenario, documentación con capturas originales, medición de resultados reales y aceptación académica formal. No asignar un porcentaje global inventado a la rúbrica.

## Matriz P0 con aceptación y capturas (22/11/2026)

[Ver matriz de aceptación de 12 historias P0](evidence/MATRIZ_ACEPTACION_P0_2026-11-22.md): **8 aceptadas QA / 2 parciales / 2 pendientes**, con evidencia E01–E12, criterio, excepción y contrato. El anexo Word contiene las 12 capturas incrustadas; no se han subido binarios a GitHub. No confundir el 66,7 % QA con el 90 % de la rúbrica.


---

## Actualización 23/11/2026 — corte formal del segundo recorrido QA

**Fuente primaria de este corte:** [ACTA_CORTE_FORMAL_SQA_E2E_2026-11-23.md](evidence/ACTA_CORTE_FORMAL_SQA_E2E_2026-11-23.md).

**Juicio profesional:** **GO** para demostración del MVP académico y continuidad de documentación QA; **NO-GO** para declaración de producción, medición de ahorro de campo o cumplimiento formal de rúbrica.

| Frente | Estado al 23/11 | Alcance de evidencia |
| --- | --- | --- |
| Operador web, optimización, sedes, asignación | **TESTED QA** | Preparación de segunda ruta cinco paradas; baseline 48,43 km y 71 min, optimizada 41,68 km/61 min, mejora indicada 14,59 % **estimada** |
| Android auth/consulta/start | **TESTED QA** | Ruta `fb413b71-...` asignada y transición PLANNED→ACTIVE, con confirmación explícita |
| US-IMP-013 deliver/fail | **TESTED QA** | Cinco paradas: **4 DELIVERED, 1 FAILED**, cero pendientes. GET Firestore directo en pedido 1 y pedido 2; otras tres por Android |
| US-V1-008 GPS | **TESTED QA SIMULADO** | Consentimiento, fix San Isidro (5 m), HTTP 200 Firestore; dato eliminado en cierre según política |
| US-IMP-014 complete | **PASS E2E Firestore** | HTTP 200 ruta COMPLETED, driver available=true, historial; HTTP 404 en reserva y último GPS |
| CI Android y QA Automation | **PASS para PR #73** | [PR #73](https://github.com/JuliusCordova/SmartRoute_AI/pull/73) integrado, commit `c309a59`. No equivale a pruebas de seguridad productiva |
| SQA/ética/seguridad | **PARCIAL** | Registro de incidencias y controles existentes; faltan negativos desplegados, revisión de permisos, trazas, evidencia completa de privacidad, accesibilidad y consentimiento |
| Indicadores OE1/OE2/OE3, piloto real | **PENDIENTE** | Sin distancia GPS real recorrida, ahorro real, puntualidad observada ni A/B comparable |
| Publicación y aceptación final | **PENDIENTE** | Falta anexar capturas saneadas, reporte final, control de calidad documental y evidencias académicas/competencias |

### Indicador QA funcional actualizado

- **10/12 P0 aceptadas (83,33 %); 1/12 parcial (8,33 %); 1/12 pendiente (8,33 %)** en [matriz fechada](evidence/MATRIZ_ACEPTACION_P0_2026-11-22.md#adenda-oficial--corte-formal-23112026-tc-e2e-qa-20261123-02). Los 12 criterios no deben equipararse al universo de controles académicos.
- **100 % de paradas resueltas** en esta ruta: 4 entregadas (80 % de éxito) y una fallida (20 %), **todo sintético**.
- **Privacidad GPS:** el documento `driver_last_locations` estuvo disponible durante ruta ACTIVE y se eliminó tras COMPLETED; no queda historial de ubicaciones de la ruta por este mecanismo.
- El resultado **14,59 % es estimado** por optimización; no inferir ahorro materializado ni cumplimiento de meta 20 %.

### Congelamiento de la ejecución y próximos gates

1. Conservar las dos rutas cerradas anteriores como evidencia histórica; **no** mutar `fb413b71-...` ni `aec305db-...`.
2. Cerrar formalmente SQA de *esta funcionalidad en QA* mediante el acta y matriz, sin modificar servicios ni publicar build de distribución.
3. P0 documental: incorporar capturas y resultados de ejecución con fecha, revisión de privacidad, hashes y trazabilidad al informe final y rúbrica.
4. P0 de ingeniería: pruebas negativas con otros UID/roles, evidencia de error/resiliencia/idempotencia y separación release/staging, sin abrir acceso de producción.
5. P0 académico: capítulos metodológico y VII resultados/evaluación económica, ética, impacto social, ambiental, legal y tecnológico, control de calidad y juicio profesional, claramente limitados a evidencia disponible.
6. P1 producto: corregir etiqueta de origen («Depósito»), defecto visual del mapa/detalle y documentar precisión/criterio GPS; **sin introducir funcionalidades nuevas durante el corte**.

**El acta constituye cierre de ejecución QA, no aceptación académica ni autorización para producción.**
