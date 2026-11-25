# US-016 — Evidencia de frontend cliente y consolidación MVP

**Fecha base:** 23/11/2026. Este documento actualiza el corte preliminar de la rama frontend con resultados obtenidos después de integrar frontend, API y gateway en el PR #84.

## Pruebas confirmadas

| Suite o escenario | Evidencia | Resultado |
|---|---|---|
| Frontend: `npm test` | Token opaco, payload permitido, ETA, estados, traversal, valores inválidos | 6/6 PASS |
| API completa: `python -m pytest -q tests/` | Incluye US-016 y regresiones backend | 106 PASS, 11 SKIPPED |
| Gateway completo: `python -m pytest -q tests/` | Incluye autenticación, CORS y tracking | 34/34 PASS |
| Pruebas específicas US-016 tras merge | 6 frontend + 5 API + 3 gateway | 14/14 PASS (subconjunto, no sumar a las 146) |
| A/B sintética por API TestClient | Tokens por pedido, revocación A y persistencia de B | PASS |
| Integración gateway → API simulada | Transporte `httpx.AsyncClient.request` sustituido, IAM ficticio | 5/5 PASS |
| Visual en Windows localhost | Pedidos A/B, token desconocido, responsive 320 × 650 px | PASS |
| Gateway staging | Solicitud POST a tracking sin habilitar feature | HTTP 404 observado |
| Logs gateway staging (muestra 24/11 UTC) | URL/path y respuesta, sin token visible en muestras revisadas | PASS limitado al intervalo |

Las suites completas totalizan **146 aprobadas, 11 omitidas, cero fallidas** en Cloud Shell. La prueba HTTP A/B mediante mocks y la web conectada al simulador **no** son una prueba real de despliegue extremo a extremo con servicios GCP.

## Contrato implementado (PR #84)

- `POST /api/v1/public/tracking` recibe `{"token":"..."}` en JSON (no GET ni token en la ruta del servidor).
- Token temporal opaco, SHA-256 persistido, revocación, vencimiento y asociación estricta a un pedido sintético; error 404 indiferenciado.
- Solo el operador autenticado puede emitir el enlace; el destinatario puede consultar sin Firebase **únicamente** el endpoint público, sujeto a feature gate.
- Respuesta de mínimo privilegio: `order_reference`, `status`, `eta_minutes` (sin ETA inventada, GPS ni datos privados).
- Políticas HTTP: `no-store`, `no-referrer`, `noindex, nofollow` en las capas correspondientes.

## Cierre MVP: estado y límites

**QA de componentes, pruebas de integración HTTP simulada y QA visual local: aprobadas.** La rama integrada `test/us016-integracion` está publicada para revisión en PR #84, sin merge ni despliegue.

Pendiente:
1. Verificar que CI y QA del commit final de PR #84 concluyan sin errores tras cambios documentales.
2. Confirmar aceptación visual respecto al prototipo y registrar decisión del responsable.
3. Definir si el MVP se presenta con simulador o con servicios controlados en staging. Si se pretende exposición externa, falta evaluación de riesgos y E2E real en entorno aislado.
4. No confundir `404` en staging con comprobación concluyente del feature gate; podría ser una revisión que aún no implemente ese endpoint.

**Decisión de alcance:** rate limiting distribuido y Cloud Armor/equivalente quedan en backlog **productivo**, no como bloqueante para aceptar las pruebas locales del MVP; esto no autoriza habilitar servicio público sin análisis.

## Evidencia adicional

- PR #81: frontend.
- PR #82: backend y gateway.
- PR #83: `docs/evidence/US016_GUIA_PRUEBA_VISUAL_LOCAL_2026-11-23.md` con receta de servidor sintético, túnel SSH de Windows, escenarios A/B, token desconocido y responsive. Las capturas se compartieron en la conversación, no se subieron como archivos binarios al repositorio.
- PR #84: integración para aceptación, actualmente no fusionada.
