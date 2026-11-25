# US-016 — Web móvil de seguimiento de pedidos (MVP)

Aplicación independiente del operador web y del conductor Android. El destinatario consulta el estado de **un único pedido** desde el móvil sin instalar aplicación ni iniciar sesión en Firebase. La web usa la ruta `/#/t/{token}` y realiza `POST /api/v1/public/tracking` con cuerpo JSON `{"token":"..."}`. No se debe utilizar el ID del pedido como token.

## Estado de implementación

- **Frontend, API y gateway implementados** en la rama integrada `test/us016-integracion` (PR #84); **no implica despliegue ni activación en GCP**.
- El backend genera tokens opacos con `secrets.token_urlsafe(32)`, conserva solo SHA-256, establece expiración de 24 h y admite revocación. Solo se permiten enlaces para órdenes marcadas `synthetic` en este incremento.
- La consulta pública se encuentra detrás del flag `SMARTROUTE_PUBLIC_TRACKING_ENABLED=true` en API y gateway, desactivada por defecto. El operador necesita Firebase; el destinatario consulta únicamente el endpoint público.
- La respuesta permite únicamente `order_reference`, `status` y `eta_minutes`. Un ETA `null` se representa como no disponible. No exponer GPS, datos del conductor, direcciones privadas, ruta completa ni otras órdenes.
- Los tokens inválidos, expirados o revocados deben devolver 404 indiferenciado. Las respuestas usan `Cache-Control: no-store`, `Referrer-Policy: no-referrer` y `X-Robots-Tag: noindex, nofollow`.
- El token en el **fragmento de URL** no se envía al servidor estático como parte del path HTTP. El frontend envía el token al backend solo mediante POST JSON. No registrar tokens en cuerpos, logs o enlaces compartidos públicamente.

## Ejecución y pruebas

```bash
cd apps/customer-tracking
npm test
```

- Frontend: 6/6 PASS; backend: 106 PASS, 11 SKIPPED; gateway: 34 PASS en Cloud Shell, al corte del 23/11/2026.
- Contrato de dos pedidos sintéticos y revocación: PASS por FastAPI TestClient.
- Gateway → API con transporte sustituido: 5/5 verificaciones PASS (sin red real).
- Vista local mediante servidor sintético + túnel SSH Windows: pedido A, pedido B, token desconocido y responsive 320 px PASS.
- La vista previa web autenticada de Cloud Shell presentó redirección y bloqueo CORS. La prueba visual aceptada utilizó `http://127.0.0.1:8081` mediante túnel SSH.
- Evidencias y receta reproducible: PR #83, `docs/evidence/US016_GUIA_PRUEBA_VISUAL_LOCAL_2026-11-23.md` en rama `docs/us016-checkpoint-20261123`.

## Pendiente de cierre / exposición

- Comparación final con el prototipo y aceptación funcional.
- Verificación controlada de infraestructura integrada (no realizada con Firebase, Cloud Run, IAM y Firestore reales); mantener deshabilitado el endpoint público mientras se decide la exposición.
- Confirmar seguridad de despliegue y canal de entrega de enlaces antes de clientes externos.
- **Rate limiting distribuido queda expresamente fuera del MVP** y forma parte del backlog productivo. Esta decisión no equivale a autorizar exposición pública irrestricta.
