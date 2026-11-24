# SmartRoute AI — checkpoint del despliegue US-016 y diagnóstico (23 nov 2026, Lima)

> Estado documentado a partir de resultados de Cloud Shell y capturas aportados en la conversación; **no es una validación de producción ni una prueba E2E aprobada**. Este documento es un punto de reanudación, sin cambios de infraestructura, tráfico ni rama `main`.

## Estado confirmado

| Servicio | Imagen US-016 | Revisión con 100% tráfico | Evidencia |
| --- | --- | --- | --- |
| API: `smartroute-api-staging` | `sha256:08d23a142f11e8cc988caae29519f9548ec000935dcd385ebf8752b57835d1f4` | `00016-flz` | `/health` a través de proxy: HTTP 200, `{"status":"ok","service":"smartroute-api"}` |
| Gateway: `smartroute-gateway-staging` | `sha256:c0dd9ba27df630f5e580f19de1b7e8abca155ff701fbe2a8cdb150cafdf209ba` | `00016-bmf` | `/health`: HTTP 200, `{"status":"ok","service":"smartroute-gateway"}`; **esto no valida /api/v1/** |
| Operador web: `smartroute-web-staging` | `sha256:8e63b135a27d14fd8b3c5883c9bfd692e1fa3f7d7338530d0626a74262b787b2` | `00010-cpl` | pantalla visible y HTTP 200; login Google visible como autenticado |
| Tracking web cliente | aún sin despliegue verificado | N/A | pendiente; no declarar MVP completo |

Proyecto: `proyectopersonal-480420`; región: `us-central1`; Firestore nombrado: `smartroute`; `SMARTROUTE_PUBLIC_TRACKING_ENABLED` no configurado/activado, mantener deshabilitado.

PR integrador **#84**, rama `test/us016-integracion`, **draft**, sin merge a `main`. Build usado: commit `c54add0`.

## Incidente observable

- En operador web se corrigió `GATEWAY_URL` de URL con etiqueta `qa-90681ae` a `https://smartroute-gateway-staging-mkqutd4koq-uc.a.run.app`.
- Se actualizó `SMARTROUTE_ALLOWED_ORIGINS` del gateway para incluir `https://smartroute-web-staging-mkqutd4koq-uc.a.run.app`.
- En la captura más reciente, después de esos cambios, siguen apareciendo `Failed to fetch`, mensajes de CORS y al menos una respuesta **HTTP 503** en la API de pedidos. Sesión Google ya iniciada.
- No hay evidencia suficiente de que la base Firestore esté vacía, ni de que las consultas autenticadas hayan alcanzado el backend.

## Hallazgo confirmado en código: desalineación de URL de backend

En `services/gateway/app/main.py` de esta misma rama:

1. `backend_url()` solo acepta valores incluidos en `APPROVED_API_URLS`; `require_config()` invoca `backend_url()` antes de comprobar Firebase y antes de enviar solicitudes HTTP.
2. `APPROVED_API_URLS` **sí** incluye `PRIVATE_API_URL = https://smartroute-api-staging-913797829604.us-central1.run.app` y algunas URLs QA etiquetadas.
3. `APPROVED_API_URLS` **no** incluye `https://smartroute-api-staging-mkqutd4koq-uc.a.run.app`, valor configurado durante este despliegue en `SMARTROUTE_BACKEND_URL`.
4. Para una solicitud `/api/v1/orders`, `require_config()` genera `RuntimeError` y el gateway la traduce en **HTTP 503** con `Gateway not configured`.
5. Las respuestas de error `HTTPException` emitidas antes del retorno exitoso de `proxy()` no añaden `Access-Control-Allow-Origin`, por lo que el navegador puede mostrar un mensaje CORS **como síntoma secundario**. `/health` no verifica esta configuración.
6. `private_id_token()` usa `PRIVATE_API_URL` como audiencia del token IAM, por lo que reutilizar esta URL aprobada es más conservador que añadir otra URL al allowlist sin evaluar audiencia/permisos.

**Nivel de certeza:** fallo de configuración/código **confirmado de manera estática**; su contribución a todos los errores observados en vivo es **hipótesis fuerte**, pendiente de verificación HTTP tras corregir la variable. Otros problemas, si los hay (IAM, rol de Firestore, autorización), podrán aflorar después.

## Reanudación mínima para la próxima sesión (solo 3 acciones)

**1. Corregir únicamente la URL del backend del gateway** a su `PRIVATE_API_URL` previamente autorizada; no reconstruir imágenes, no cambiar `main`, no modificar CORS ni activar tracking público:

```bash
gcloud run services update smartroute-gateway-staging \
  --project=proyectopersonal-480420 \
  --region=us-central1 \
  --update-env-vars=SMARTROUTE_BACKEND_URL=https://smartroute-api-staging-913797829604.us-central1.run.app
```

Como el tráfico está anclado a revisiones manualmente, **antes de probar** identificar la nueva revisión lista, confirmar imagen y variable y asignarle tráfico si quedó al 0%. Evitar usar únicamente el nombre `latestReadyRevisionName` como prueba de tráfico.

**2. Una sola prueba CORS real:** confirmar `OPTIONS` a `/api/v1/orders` con `Origin: https://smartroute-web-staging-mkqutd4koq-uc.a.run.app`, `Access-Control-Request-Method: GET` y `Access-Control-Request-Headers: authorization` devuelve `204` y `Access-Control-Allow-Origin` exactamente igual al origen. Si falla, investigar revisión/config CORS; no seguir con el navegador.

**3. Una prueba de negocio:** refrescar tablero una sola vez con sesión Google y revisar en DevTools `Network` códigos de `/api/v1/orders`, `/api/v1/optimized-routes` y `/api/v1/distribution-centers`. Si devuelve `401/403`, diagnosticar token/rol/IAM; si `502/503`, consultar logs Cloud Run por revisión, sin copiar cabeceras de autorización. No crear datos ni modificar Firestore antes de identificar el error.

**Criterio de cierre:** solicitudes del navegador sin bloqueo CORS, respuestas API válidas (aunque listas vacías) y evidencia E2E autenticada. La pantalla de tracking cliente y su mapa siguen siendo trabajo pendiente; no afirmar funcionalidad completa.

## No hacer

- No volver a compilar ni desplegar API, gateway y web simultáneamente.
- No habilitar `SMARTROUTE_PUBLIC_TRACKING_ENABLED` sin pruebas específicas.
- No hacer merge de PR #84 ni modificar `main` por este incidente.
- No publicar Firebase tokens, Authorization o datos reales en evidencias.
- No interpretar `/health=200` como prueba de integración API/Firestore.
