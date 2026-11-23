# US-016 — Corte técnico de pruebas (2026-11-23)

## Alcance y criterio
Seguimiento web móvil del destinatario, independiente del operador y Android. Acceso con token opaco temporal asociado a un solo pedido, sin autenticación Firebase del destinatario. No exponer GPS, dirección privada, conductor ni otras órdenes. No inventar ETA. Alcance excluido por decisión del proyecto: semáforo de puntualidad, modo sin conexión, deshacer y exportar resultados.

## Evidencia ejecutada en Google Cloud Shell
| Suite | Resultado |
|---|---|
| `apps/customer-tracking && npm test` | 6 aprobadas |
| `services/api && python -m pytest -q tests/` | 106 aprobadas, 11 omitidas |
| `services/gateway && python -m pytest -q tests/` | 34 aprobadas |
| **Total de suites completas** | **146 aprobadas, 11 omitidas, 0 fallidas** |

Las 14 pruebas específicas (6 frontend + 5 API + 3 gateway) se volvieron a ejecutar y pasaron en la rama local **`test/us016-integracion`** luego de combinar las ramas cliente y backend. Son un subconjunto de las 146, no pruebas adicionales.

## Prueba A/B sintética por FastAPI TestClient
- Dos órdenes sintéticas con UUID, estado `IN_TRANSIT` y `FAILED`.
- Dos tokens distintos, consultas separadas por endpoint `POST /api/v1/public/tracking`.
- Se verificó correspondencia de referencia/estado y respuesta acotada a `order_reference`, `status`, `eta_minutes` (null).
- Revocar token A devolvió 404; token B siguió disponible.
- Base de datos simulada en memoria; **no demuestra E2E real con gateway, Firestore ni navegador**.

## UI / simulador HTTP
- Servidor web estático y simulador local `127.0.0.1:8081` iniciados en Cloud Shell.
- Pantalla de enlace inválido renderizada en escritorio y en vista móvil de 320 px; no se apreció desbordamiento horizontal.
- `curl` HTTP directo a `/api/v1/public/tracking` con token ficticio devolvió 200 y `{"order_reference":"SR-DEMO-A","status":"IN_TRANSIT","eta_minutes":null}`.
- **Bloqueador**: en la vista previa de navegador con `#/t/<token>` la pantalla muestra «No se pudo consultar» y en los logs del simulador no se observa un POST. Pendiente investigar consola/red de Chrome y posible interferencia de vista previa de Cloud Shell; no atribuir causa sin evidencia.
- `favicon.ico` 404 inocuo.
- El README y un comentario de `main.js` siguen describiendo el backend como pendiente, aunque ya se implementó en rama separada. Actualizar al integrar.

## Estado de Git y despliegue
- PR #81 `feat/us016-customer-tracking-web`: abierto en borrador, no fusionado.
- PR #82 `feat/us016-public-tracking-backend-gated`: abierto en borrador, no fusionado.
- En Cloud Shell se creó `test/us016-integracion` desde backend y se fusionó `test/us016-cliente` sin conflictos tras recuperar historial con `git fetch --unshallow`. **Esta rama integrada es local y NO se ha subido a GitHub**.
- Archivos no versionados preexistentes `apps/operator-web/dist/`, `node_modules/`, `package-lock.json` quedaron sin tocar.
- `main` sin modificar por estas pruebas. No se desplegó nada a Cloud Run ni se operó sobre Firestore real. Feature gate del seguimiento público desactivado por defecto.
- **Este documento es un checkpoint remoto de estado basado en la rama backend, NO contiene el merge local de frontend + backend**.

## Próximas acciones al retomar
1. Revisar error de navegador (DevTools Console y Network): confirmar si llega el POST desde la UI a la misma URL/origen. Evitar enlaces de demo publicados en espacios públicos.
2. Verificar estados visuales de pedido `IN_TRANSIT` y `FAILED`, junto con errores, en pantalla móvil.
3. Preparar integración versionada en GitHub de frontend, backend y gateway, sin afectar `main`; actualizar documentación desfasada.
4. E2E aislado con emulador de Firestore/gateway y controles: token inválido, expirada, revocación, IDOR, rate limiting, logging seguro y CORS.
5. Solo después decidir despliegue controlado y revisión visual frente al prototipo. No anunciar US-016 como producción lista.

Referencias: PR #81 https://github.com/JuliusCordova/SmartRoute_AI/pull/81 ; PR #82 https://github.com/JuliusCordova/SmartRoute_AI/pull/82.
