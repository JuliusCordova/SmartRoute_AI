# Evidencia: gateway privado /health autenticado IAM — HTTP 200

Después de validar `HTTP 403` para una petición anónima a `/health` (véase `docs/GCP_GATEWAY_ANONYMOUS_HTTP_403_PASS.md`), el propietario abrió un `gcloud run services proxy` autenticado para `smartroute-gateway-staging` y ejecutó:

```bash
curl -i --max-time 15 http://127.0.0.1:18080/health
```

Respuesta real:

```http
HTTP/1.1 200 OK
Content-Length: 46
Content-Type: application/json
Server: Google Frontend

{"status":"ok","service":"smartroute-gateway"}
```

Fecha de respuesta en cabecera: `Wed, 04 Nov 2026 02:58:58 GMT`. Esto comprueba la disponibilidad del endpoint protegido utilizando identidad autenticada mediante el proxy de Cloud Run. **No demuestra aún** Firebase ID-token verification, roles en Firestore ni llamadas autenticadas al backend.

## Continuación: pruebas negativas Firebase sin mutaciones
Con el proxy IAM abierto, desde otra terminal:

```bash
BASE=http://127.0.0.1:18080
curl -sS -i --max-time 15 "$BASE/api/v1/orders"
curl -sS -i --max-time 15 -H 'Authorization: Bearer token-invalido-de-prueba' "$BASE/api/v1/orders"
```

Ambas respuestas deberían devolver `HTTP 401` de la aplicación, una por falta de Firebase bearer token y otra por token inválido. Si ocurre `403/503` u otro código, detener la prueba y diagnosticar capa IAM/proxy/configuración. Las consultas son `GET` y no crean registros.

No abrir el gateway públicamente todavía; proyecto compartido, no alterar otras apps, Firebase sign-in providers ni Firestore `(default)`/`gestioncitas`. `GCP_STAGING_ENABLED=false`.
