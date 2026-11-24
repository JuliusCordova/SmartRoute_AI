# SmartRoute AI — incidente y solución: autenticación del tablero US-016 (24 nov 2026)

**Estado: RESUELTO en staging según validación visual autenticada.** El tablero pasó de `Failed to fetch` / CORS / HTTP 401-503 a **«Centro de control conectado: 23 pedidos y 4 rutas recuperadas»**. La captura de cierre también muestra **23 pedidos**, **82.4 % de efectividad** y el filtro **«En recorrido»** con **0 rutas** (coherente con el filtro activo; no confundir con las 4 rutas recuperadas). Evidencia visual aportada en la conversación el 24/11/2026; **imagen no adjunta como archivo binario a este commit**.

## Alcance y condiciones

- Proyecto GCP: `proyectopersonal-480420`; región: `us-central1`; Firestore nombrado: `smartroute`.
- Servicios desplegados: API `smartroute-api-staging`, gateway `smartroute-gateway-staging`, operadores `smartroute-web-staging`.
- PR #84, rama `test/us016-integracion`, permaneció en draft sin merge de `main` durante la resolución.
- No se realizaron cambios de código para resolver este incidente. Sí se aplicaron ajustes de configuración Cloud Run y roles IAM.
- Este cierre **no** significa que el seguimiento web de clientes US-016 ni su paridad con el prototipo estén desplegados o aceptados.

## Síntomas y diagnóstico por capas

| Síntoma | Causa técnica identificada | Acción aplicada | Comprobación |
| --- | --- | --- | --- |
| Navegador: `auth/unauthorized-domain` | Dominio principal de staging no autorizado en Firebase Auth | Autorizar dominio exacto del frontend en Firebase Authentication | Capturas posteriores muestran sesión iniciada |
| Tablero: `Failed to fetch` y mensajes CORS | El operador web llamaba al gateway etiquetado `qa-90681ae`; el origen actual del frontend no constaba entre los permitidos por el gateway | Ajustar `GATEWAY_URL` a servicio principal; agregar dominio de web principal a `SMARTROUTE_ALLOWED_ORIGINS`; desplegar revisiones y verificar tráfico | `OPTIONS /api/v1/orders` -> HTTP 204, `Access-Control-Allow-Origin` exacto |
| Gateway: HTTP 503 | `SMARTROUTE_BACKEND_URL` estaba configurado con URL `...-mkqutd4koq-uc.a.run.app` no incluida en `APPROVED_API_URLS` de `services/gateway/app/main.py` | Cambiar a URL aprobada `https://smartroute-api-staging-913797829604.us-central1.run.app` y activar revisión `smartroute-gateway-staging-00017-66z` al 100 % | Desapareció el 503 inicial de configuración; aparecieron errores siguientes de identidad |
| Gateway: HTTP 401 al consultar pedidos y rutas | `verified_firebase_token()` ejecuta `auth.verify_id_token(..., check_revoked=True)`; la cuenta `smartroute-gateway` no tenía `roles/firebaseauth.viewer` sin condición | Conceder `roles/firebaseauth.viewer` sin condición de Firestore a `smartroute-gateway@proyectopersonal-480420.iam.gserviceaccount.com` | Después las solicitudes alcanzaron la API y emergió `503 Identity service unavailable` |
| API: HTTP 503 «Identity service unavailable» | `services/api/app/auth.py::current_user()` también valida Firebase con `check_revoked=True`, además de leer perfiles en Firestore. La cuenta `smartroute-runtime` tampoco tenía el rol de lectura de Firebase Auth sin condición. El mensaje 503 engloba otras excepciones; el rol es la explicación más fuerte según secuencia | Conceder `roles/firebaseauth.viewer` sin condición a `smartroute-runtime@proyectopersonal-480420.iam.gserviceaccount.com` | **Éxito de extremo a extremo visible:** 23 pedidos y 4 rutas recuperadas; sesión Google autenticada; métricas calculadas |

### Detalle crítico de IAM

El primer intento de asignar `roles/firebaseauth.viewer` al gateway heredó por selección interactiva la condición `SmartRouteDbOnly`, expresión `resource.name == 'projects/proyectopersonal-480420/databases/smartroute'`. Esa condición pertenece al recurso Firestore, por lo que no corresponde a operaciones de usuarios de Firebase Authentication.

Se corrigió explícitamente con `--condition=None --quiet` para ambas cuentas:

```bash
gcloud projects add-iam-policy-binding proyectopersonal-480420 \
  --member="serviceAccount:smartroute-gateway@proyectopersonal-480420.iam.gserviceaccount.com" \
  --role="roles/firebaseauth.viewer" --condition=None --quiet

gcloud projects add-iam-policy-binding proyectopersonal-480420 \
  --member="serviceAccount:smartroute-runtime@proyectopersonal-480420.iam.gserviceaccount.com" \
  --role="roles/firebaseauth.viewer" --condition=None --quiet
```

La política IAM entregada tras ambos comandos muestra ambos miembros en binding **sin condición** y el binding original del gateway **con condición SmartRouteDbOnly** aún presente. Queda como limpieza posterior remover **solo** el binding condicional redundante (sin tocar el rol sin condición ni `roles/datastore.user` de `smartroute-runtime`).

No se debe quitar `check_revoked=True` para ocultar errores de permisos. El rol viewer es de lectura y se concede a nivel proyecto para Firebase Auth; el rol `roles/datastore.user` de la API conserva su condición sobre la base Firestore nombrada.

## Evidencia de aceptación (24/11/2026)

1. Backend API: `GET /health` por Cloud Run proxy -> `200`, servicio `smartroute-api`.
2. Gateway: `GET /health` -> `200`, servicio `smartroute-gateway`.
3. CORS navegador: preflight `OPTIONS /api/v1/orders?limit=50` -> `HTTP/2 204` con `Access-Control-Allow-Origin: https://smartroute-web-staging-mkqutd4koq-uc.a.run.app`.
4. IAM: respuestas `gcloud projects add-iam-policy-binding` con `Updated IAM policy`, y bindings Firebase Auth viewer sin condición para ambas service accounts.
5. Prueba funcional final: pantalla de operador autenticado, barra `Centro de control conectado: 23 pedidos y 4 rutas recuperadas`, contador `PEDIDOS 23`, efectividad `82.4 %`, sin banner de error. No inventar métricas adicionales; `RUTAS 0` en tarjeta corresponde al filtro `En recorrido` aplicado.

## Recomendaciones para evitar recurrencia

1. Documentar en configuración desplegable el **dominio exacto del frontend**, URL de gateway principal y URL aprobada del backend / audiencia IAM; no dejar endpoints QA etiquetados como destino por defecto.
2. Incorporar comprobación de arranque o smoke test autenticado, porque `/health` por sí solo no valida permisos ni el camino Firebase → Gateway → IAM → API → Firestore.
3. Revisar que los errores de autenticación del gateway mantengan cabeceras CORS para orígenes explícitamente aprobados, sin filtrar información interna ni tokens; actualmente errores previos al return exitoso pueden parecer fallos CORS.
4. Mantener revisión de mínimos privilegios y distinguir permisos `firebaseauth.*` de permisos Firestore en IAM Conditions; limpiar el binding condicional redundante del gateway cuando se planifique.
5. Conservar la prueba final mediante sesión de operador con datos sintéticos; no afirmar que hay datos productivos.

## Pendientes no cubiertos por este cierre

- Frontend público de seguimiento de clientes US-016 y paridad visual con prototipos: pendiente de publicar/validar.
- Pruebas E2E específicas de seguimiento por token temporal, expiración y revocación en staging real: pendientes. `SMARTROUTE_PUBLIC_TRACKING_ENABLED` debe mantenerse desactivado hasta superar aceptación.
- Verificación posterior de operación real, Android y otras historias según SDD: no inferir a partir de esta prueba.
- Mantener PR #84 sin merge hasta decisión explícita.

---

## Registro anterior (23/11/2026, incidente aún abierto)

> Se conserva el diagnóstico histórico tal como estaba; sus secciones «incidente observable», «reanudación mínima» y «criterio de cierre» describen la situación **antes de la resolución del 24/11**, no tareas que sigan pendientes.

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
