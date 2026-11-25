> **ACTUALIZACIÓN 25/11/2026:** Tras esta acta se añadieron dos evidencias de cierre: [US-011 comparación visual validada](evidence/US011_COMPARACION_VISUAL_VALIDADA_2026-11-25.md) y [SEC-01 revocación QA en Gateway staging](evidence/SEC01_REVOCACION_REAL_STAGING_2026-11-25.md), donde se documenta la secuencia **403 antes, revocación registrada, 401 después** y sus límites. Los pendientes descritos más abajo reflejan el corte **anterior a estas pruebas**. Los archivos binarios de capturas y el APK siguen sin estar adjuntos al repositorio.\n\n# Acta de cierre del MVP académico — SmartRoute AI

**Fecha:** 25/11/2026 · **Proyecto:** Capstone UPN, período de 7 semanas.

## Integración del repositorio

- PR [#84](https://github.com/JuliusCordova/SmartRoute_AI/pull/84) integrado en `main`, commit de merge **`1c9104fd870e707fbbc041038fd32f5ee47e164e`**.
- Head de integración antes de merge: `548768f713a9a86438c2114cacdf79d32aaba16d`.
- Para ese head, GitHub Actions **SmartRoute CI and automated staging** (run `45541282689`) y **SmartRoute QA Automation** (run `45541282667`) concluyeron **success**. Esto no certifica que todos los gates funcionales/seguridad E2E hayan sido ejecutados.
- El merge no es un nuevo despliegue de Cloud Run y no adjunta automáticamente archivos binarios de capturas ni APK.

## Evidencias del MVP

| Subsistema | Resultado soportado |
| --- | --- |
| Backend + Gateway | Servicios staging accesibles en los flujos ya probados; integración US-016 con limitación de información pública y controles por token |
| Web de operador | Cloud Run revisión `smartroute-web-staging-00012-ztd` con tráfico 100% confirmado en sesión; login autenticado, 23 pedidos, 4 rutas, dashboard y mapa de operaciones |
| US-011 métricas / DEF-01 | Comparación estimada en tabla de 4 rutas; porcentajes actuales consistentes con segundos exactos y etiqueta explícita de datos **estimados** |
| Cliente web US-016 | Flujo operador → enlace temporal → destinatario sin login validado visualmente con datos sintéticos; token revocable / expirable implementado |
| Android repartidor | Gradle `assembleDebug` en Windows **BUILD SUCCESSFUL**, APK debug **33 070 890 bytes** (24/11 22:04:49), instalación ADB en emulador `emulator-5554` **Success**; interfaz de listado y detalle de ruta comprobadas por capturas |
| Recorrido Android | Ruta `fb413b71...`: 5/5 paradas **atendidas**, 4 entregadas, 1 no entregada, distancia y tiempo **estimados**; no inferir 100% de entregas exitosas |

## Alcance y reservas de aceptación

- **Excluidos del MVP:** Gemini consultivo US-012, offline US-013/014, piloto de campo US-015, deshacer entrega, semáforo de puntualidad y exportación; son mejoras futuras, no entregables bloqueados. Ver `docs/decisions/CR-2026-11-24-02_US012_US015_MEJORAS_FUTURAS.md`.
- **SEC-01:** `check_revoked=True` en gateway y API y pruebas unitarias agregadas; **no consta prueba E2E de un Firebase ID token realmente revocado en staging**. Dejar este gate de seguridad expresamente pendiente antes de declarar el sistema listo para producción.
- **DEF-01:** cifras actuales y presentación de tiempos validadas; la cifra histórica **19,43%** del 15/11 no fue auditada contra JSON original de segundos.
- **Comparación de trazado doble:** código incorporado y panel desplegado, pero **no consta captura de vista previa con línea base y optimizada simultáneas**; el mapa visualizado en sesión era una ruta persistida.
- **Evidencia binaria:** las capturas se aportaron en conversación pero **no están incluidas como binarios en GitHub**; el APK debug está en la laptop del autor, no publicado como artefacto GitHub. Esto debe revisarse antes de entrega académica si el docente exige anexos o un instalable accesible.
- **Producción:** las evidencias corresponden a **staging y emulador**, datos sintéticos y estimaciones; no son una certificación de producto listo para clientes reales, medición de ahorro real, GPS de campo o fiabilidad productiva.
- **Ponderación:** alcance nominal revisado de 53 puntos, pero **no hay porcentaje global oficialmente reconciliado** tras exclusiones; evitar reportar porcentajes provisionales como medidos o certificados.

## Estado de cierre

**MVP académico integrado en `main` y con funcionalidad central demostrada.** El cierre del repositorio y el de la integración técnica son distintos del cierre de la documentación entregable y de la certificación de seguridad para producción. Los límites señalados deben trasladarse al informe académico.

### Referencias de trazabilidad

- `docs/checkpoints/CORTE_VISUAL_ANDROID_OPERADOR_DEF01_2026-11-24.md`
- `docs/evidence/DEF01_PORCENTAJE_MEJORA_REDONDEO_2026-11-23.md`
- `docs/evidence/SEC01_FIREBASE_TOKEN_REVOCATION_2026-11-23.md`
- `docs/evidence/US016_CUSTOMER_TRACKING_QA_2026-11-23.md`
