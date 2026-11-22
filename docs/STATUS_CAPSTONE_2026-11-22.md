# SmartRoute AI — Estado del Capstone al 22/11/2026

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
