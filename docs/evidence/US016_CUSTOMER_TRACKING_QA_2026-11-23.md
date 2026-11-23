# US-016 — Corte de pruebas de frontend cliente (23/11/2026)

## Alcance ejecutado
Se ejecutó **localmente**, con Node.js **22.16.0**, una copia fiel de `tracking.js` y `tests/tracking.test.js` recuperados de la rama `feat/us016-customer-tracking-web` en GitHub. Comando: `npm test` desde `apps/customer-tracking`.

**Resultado: 6/6 PASS; 0 FAIL.**

| Prueba | Resultado |
|---|---|
| Token opaco: formato y rechazo de traversal | PASS |
| Proyección de campos permitidos (sin driver_id/GPS/otras órdenes) | PASS |
| Estado desconocido y ETA ausente | PASS |
| Payload inválido y estados especiales `constructor`, `__proto__` | PASS |
| ETA inválida y ausencia de ETA en estados no EN CAMINO | PASS |
| Longitud mínima/máxima y caracteres del token | PASS |

**Límite de evidencia:** son tests puros de frontend. NO demuestran que el backend limite acceso a un pedido, ni validez criptográfica/expiración del token, ni cumplimiento E2E de privacidad. El endpoint `GET /api/v1/public/tracking/{token}` aún está pendiente. No existe enlace de cliente desplegado ni se han consultado pedidos reales.

## Protocolo de aceptación E2E pendiente, sin tocar QA histórico
1. Desplegar servicio de prueba aislado tras code review; usar **solo pedidos sintéticos** A y B.
2. Generar tokens A y B mediante CSPRNG y persistir únicamente hash, pedido asociado y vencimiento; el enlace no debe contener order_id.
3. `GET /api/v1/public/tracking/{token_A}` devuelve únicamente proyección del pedido A. Verificar que no aparezcan datos del pedido B, identidad del conductor, coordenadas, ruta u otra PII.
4. Token B devuelve solo pedido B. Token inválido, revocado y expirado responde 404 genérico. Confirmar que listados `/api/v1/orders` exigen Firebase y RBAC.
5. Respuestas cliente con `Cache-Control: no-store`, `Referrer-Policy: no-referrer`, `X-Robots-Tag: noindex,nofollow`; anti-enumeración, límites de peticiones, no registrar tokens en claro ni en logs.
6. Abrir enlace A en navegador privado de Android/iPhone: debe cargar sin login, mostrar solo estado y ETA si existe; verificar responsive y legibilidad.
7. Validar errores de red y refresh; no mostrar datos antiguos como actuales. Revocar enlace y comprobar que deja de funcionar.
8. Ejecutar suites del operador y Android, confirmar no regresión y capturar screenshots del diseño según HTML del prototipo.

## Bloqueantes
- Backend público tokenizado, expiración y autorización **no implementados**.
- Routing web `/t/{token}`, CI de la aplicación cliente, prueba browser real y despliegue QA **pendientes**.
- No declarar historia US-016 terminada ni usar enlaces reales hasta cerrar el gate SEC.
