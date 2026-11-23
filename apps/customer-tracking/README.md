# US-016: vista web móvil para destinatario (frontend, no habilitada)

Aplicación independiente del operador y Android, con el mismo backend propuesto. La página `/#/t/{token}` se abre desde el teléfono sin instalar una app ni iniciar sesión. No enlazar todavía a clientes: falta el backend de seguimiento seguro y el enrutamiento de Cloud Run.

## Contrato propuesto (no implementado aún)
`POST /api/v1/public/tracking` con cuerpo JSON `{ "token": "..." }` con token opaco aleatorio de alta entropía asociado a **un** pedido; token hasheado en repositorio, expiración definida, revocación, rate limiting y pruebas IDOR. Nunca usar `order_id` como token. Respuesta permitida:
```json
{"order_reference":"SR-2038","status":"IN_TRANSIT","eta_minutes":null}
```
El servidor no debe devolver otras órdenes, `driver_id`, ruta completa, GPS preciso, dirección ajena ni PII innecesaria. Si el token es inválido, expirado o revocado responder indistinguiblemente 404; `Cache-Control: no-store`, `Referrer-Policy: no-referrer`, `X-Robots-Tag: noindex, nofollow`. En el frontend `eta_minutes=null` se presenta como no disponible. No simular ETA ni eventos. Definir expiración y mecanismo de envío con el responsable antes de exponer enlaces.

El enlace recomendado `/#/t/{token}` usa un fragmento que no se envía al servidor web ni se incorpora al path de logs HTTP. La infraestructura sirve `index.html` en `/` y reenvía `POST /api/v1/public/tracking` al gateway seguro bajo el mismo origen. No registrar cuerpos JSON ni tokens. Mantener encabezados anti-caché y políticas restrictivas. El cliente no tiene acceso a las credenciales Firebase del operador.

Pruebas locales: `cd apps/customer-tracking && npm test`. Esto no valida el backend, el despliegue ni la seguridad E2E.
