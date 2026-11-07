# SmartRoute AI — UX, seguridad y prototipo Android (07-11-2026)

**Estado:** decisiones de diseño aprobadas como baseline para implementación; **el HTML es prototipo navegable con datos sintéticos y sin backend**. No confundir controles diseñados con controles probados/desplegados.

**Artefacto:** [Prototipo navegable del repartidor y panel del operador](prototype/index.html). Especificación funcional fuente: [SPEC](../specs/SPEC.md); decisiones [ADR-09 a ADR-12](ADR.md). Plataforma de destino: **Flutter Android** para repartidor y **React** para operador, conectados mediante Firebase Auth → gateway → FastAPI privado → Firestore `smartroute`. El prototipo HTML no es un APK ni la aplicación final.

## Decisiones de arquitectura y UX

| ID | Decisión | Criterio verificable |
|---|---|---|
| ADR-09 | Registrar una entrega desde la lista en **un toque**, con **Deshacer** durante 6 segundos; sin diálogo de confirmación rutinario. | RNF-05, AC-005; si el evento ya fue confirmado no revertirlo solo en cliente: corrección supervisada por operador |
| ADR-10 | Consentimiento GPS explícito **previo** al permiso del sistema, no preseleccionado, revocable y opcional para completar rutas; posición solo durante ruta `ACTIVE`, última posición y nunca enviada a IA. | AC-006/007; pruebas de rechazo, revocación y fin de ruta |
| ADR-11 | Eventos offline en cola local cifrada con Android Keystore; reenvíos conservan la misma `Idempotency-Key`, banner de pendientes, limpieza tras confirmación o cierre de sesión. | AC-016; sin duplicados tras reconexión |
| ADR-12 | Línea base de UX y amenazas: Nielsen H1–H10, OWASP Top 10 Web 2025, Mobile Top 10 2024, Agentic Top 10 y LLM Top 10 2025. | matriz de riesgos, controles y evidencia por PR |

Otras decisiones: fallos de entrega con motivo de lista cerrada y comentario ≤140 caracteres; validación adicional en servidor; última posición marcada obsoleta después de 2 minutos; publicación de ruta con confirmación; separar datos `synthetic`, `estimated` y `observed` sin agregarlos; nunca presentar mejora ≤0 como ahorro; ante matriz incompleta devolver 422 `ROUTE_INFEASIBLE`; mostrar minutos/km/% con procedencia y huella de matriz. Todo texto variable de la interfaz requiere escape seguro.

## Flujo Android aprobado como referencia de interfaz

1. **Inicio:** Google Sign-In vía Firebase; backend valida UID y rol `DRIVER` activo, sin confiar en permisos del cliente.
2. **Consentimiento:** opción aceptar/rechazar GPS y cambiarla desde Cuenta; ejecución de ruta posible sin compartir ubicación.
3. **Mi ruta:** progreso, próxima parada destacada, orden optimizado y mapa; navegación detallada en Google Maps.
4. **Entrega:** un toque para `DELIVERED`, aviso para deshacer hasta 6 s y confirmación de servidor idempotente.
5. **Fallo:** motivo obligatorio, nota opcional acotada, estado `FAILED`.
6. **Sin conexión:** cola cifrada, recuento de eventos, sincronización controlada e idempotencia.
7. **Cuenta y cierre:** revocar consentimiento, cerrar sesión, borrar datos locales sensibles y dejar de transmitir GPS.

**Panel operador:** pedidos → ruta borrador → comparación base/optimizada → publicación → seguimiento → KPI OE1/OE2/OE3 → Gemini solo consultivo. El prototipo simula todas estas pantallas; no persiste pedidos ni obtiene ubicaciones reales.

## Riesgos por capa y requisitos de control

| Superficie | Baseline y controles | Evidencia pendiente |
|---|---|---|
| UX Nielsen H1–H10 | visibilidad de estado, lenguaje claro, prevención y recuperación de errores, consistencia app-panel, opciones visibles, acciones rápidas, ayuda | evaluación heurística con 3–5 personas (severidad 0–4) y prueba de entrega con repartidor |
| Web/API OWASP 2025 | RBAC en servidor, allowlist del gateway, CORS explícito, validación Pydantic, Firestore aislado, TLS, trazabilidad | pruebas E2E de autorización y despliegue, análisis de dependencias y logs |
| Mobile OWASP 2024 | token en almacén seguro, no secretos en APK, HTTPS, permiso GPS revocable, cifrado Android Keystore, R8/Play Integrity, `allowBackup=false` en release | implementación Flutter, checklist MASVS L1, pruebas instrumentadas |
| Gemini LLM/Agentic | sin herramientas de escritura, sin PII, solo KPI verificados, `action_taken=false`, respuesta con fuentes/limitaciones, tope propuesto de 20 consultas/día | golden set y verificación de 0 escrituras y 0 KPI inventados |
| Agentes de desarrollo | SPEC→branch→PR→CI→revisión humana; WIF y cuentas acotadas; nunca operar producción sin aprobación | reglas de rama, auditoría de CI y permisos reales |

**No homologar como “OK” en ejecución las marcas didácticas del HTML**. La prueba local del backend obtuvo **25 passed, 2 skipped**; los dos casos omitidos dependen de emulador. El gateway está desplegado y tiene CORS configurado para `http://localhost:8080`, pero la invocación Cloud Run seguía devolviendo 403 antes del cambio IAM. Esa brecha no se considera resuelta por este documento.

## Brechas de seguridad para backlog

| ID | Brecha | Acción y aceptación |
|---|---|---|
| SEC-01 | `check_revoked=False` en gateway/API | diseñar verificación de revocación y test token revocado→401, revisando latencia y manejo de indisponibilidad |
| SEC-02 | faltan controles de dependencias/SAST | `pip-audit`, Dependabot, CodeQL con checks visibles |
| SEC-03 | GitHub Actions usan tags movibles | fijar acciones por SHA y documentar versiones |
| SEC-04 | falta request ID transversal | correlación en gateway y API, logs estructurados sin PII, prueba en staging |
| SEC-05 | aplicación Flutter sin evidencia funcional | checklist MASVS L1 + flujo DRIVER/orden de ruta/entrega/GPS comprobado |
| INT-01 | gateway devuelve 403 a `/health` | verificar autorización de invocación antes de habilitar acceso; proteger endpoints Firebase y mantener backend privado |
| INT-02 | integración UI→API→Firestore pendiente | creación y consulta E2E de pedido sintético por OPERATOR |

## Secuencia de implementación

1. **Vertical slice operador**: finalizar gateway, proteger recursos y lograr POST/GET pedidos E2E.
2. **Android Flutter a partir del prototipo**: login `DRIVER`, ruta propia, registro de entregas y consentimientos.
3. **Optimización**: Google Routes Matrix + OR-Tools + comparación reproducible + Maps.
4. **Offline/GPS/observabilidad** y después métricas de piloto.
5. **Gemini consultivo** únicamente después del P0.

Regla de avance: cada historia entrega código, tests, demo, trazabilidad de criterio de aceptación y evidencia; un mock visual no prueba una funcionalidad real.

## Referencias de diseño

[Nielsen 10 heurísticas](https://www.nngroup.com/articles/ten-usability-heuristics/) · [OWASP Top 10](https://owasp.org/www-project-top-ten/) · [OWASP Mobile Top 10](https://owasp.org/www-project-mobile-top-10/) · [OWASP GenAI](https://genai.owasp.org/) · [SECURITY_PRIVACY](SECURITY_PRIVACY.md).
