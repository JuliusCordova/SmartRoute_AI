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

## Matriz P0 con aceptación y capturas (22/11/2026)

[Ver matriz de aceptación de 12 historias P0](evidence/MATRIZ_ACEPTACION_P0_2026-11-22.md): **8 aceptadas QA / 2 parciales / 2 pendientes**, con evidencia E01–E12, criterio, excepción y contrato. El anexo Word contiene las 12 capturas incrustadas; no se han subido binarios a GitHub. No confundir el 66,7 % QA con el 90 % de la rúbrica.


## Actualización de avance — Dashboard WOW y ruta nueva de cinco pedidos (22/11/2026)

**Nuevo corte documentado:** [QA Dashboard WOW, US-004, US-017 y conductor asignado](evidence/CORTE_QA_WOW_SEDES_RUTA_CONDUCTOR_2026-11-22.md).

- Despliegues QA etiquetados sin tráfico principal: API `00016-siq`; Gateway `00018-yek`; Web `00010-jef`. Gateway `/health` HTTP 200 y preflight CORS HTTP 204; login Firebase QA corregido mediante autorización del dominio y lectura autenticada comprobada.
- Dashboard ejecutivo con 18 pedidos, 3 rutas, efectividad 83,3 % y mejora estimada 15,0 %. Filtro ejecutivo `Finalizadas` muestra 2 rutas y mejora estimada 13,6 %.
- **US-V1-004**: filtros `No entregados` 2/18, `Entregados` 10/18, `Todos` 18/18: **PASS QA funcional**. Estado P0 de referencia actualizado en adenda de matriz (9 aceptadas/1 parcial/2 pendientes, con alcance limitado).
- **US-017**: catálogo de tres sedes, búsqueda, edición, desactivación de SEDE-NORTE (inactiva), selección de SEDE-SUR; optimización con OR-Tools/ORS y vínculo al centro de distribución guardado: **PASS QA funcional**.
- Ruta nueva `fb413b71-c963-570f-be61-500e9eadfb7b`: 5 pedidos, SEDE-SUR San Isidro, 71→61 min y 48,43→41,68 km, mejora estimada 14,59 %. Persistencia `PLANNED` y posterior **asignación al conductor QA** verificadas visualmente. **La ruta sigue PLANNED, no iniciada.**
- **Próximo paso:** recibir esta nueva ruta en Android con identidad del conductor QA; después realizar pruebas GPS `ACTIVE` con consentimiento y registrar evidencias. **US-V1-008, tiempos reales, puntualidad y piloto comparable siguen pendientes.**
- Observación de UI: la secuencia guardada termina con `Depósito` aunque el catálogo usa `Centro de distribución`; corregir posteriormente.

**Este agregado no convierte el staging QA en producción**, no acredita ahorro real ni incorpora los PNG originales al repositorio.
