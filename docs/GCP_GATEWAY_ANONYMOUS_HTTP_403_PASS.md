# Evidencia: gateway SmartRoute rechaza petición HTTP anónima

**Servicio:** `smartroute-gateway-staging`
**Proyecto:** `proyectopersonal-480420`
**Región:** `us-central1`
**URL Cloud Run obtenida directamente de status:** `https://smartroute-gateway-staging-mkqutd4koq-uc.a.run.app`
**Revisión existente:** `smartroute-gateway-staging-00001-bq9`
**Runtime SA:** `smartroute-gateway@proyectopersonal-480420.iam.gserviceaccount.com`

El propietario ejecutó desde Cloud Shell, **sin un token IAM**:

```bash
PROJECT=proyectopersonal-480420
REGION=us-central1
SERVICE=smartroute-gateway-staging
URL="$(gcloud run services describe "$SERVICE" --project="$PROJECT" --region="$REGION" --format='value(status.url)')"
HTTP_CODE="$(curl -sS -o /dev/null -w '%{http_code}' --max-time 15 "$URL/health")"
echo "$HTTP_CODE"
```

**Resultado real:** `403`; `PASS: acceso anónimo rechazado`.

Esto prueba **solo** que la petición anónima directa se rechaza en esta URL, no prueba permisos de todos los demás principals, flujo Firebase, conectividad a backend ni autorización OPERATOR. Política IAM directa del gateway `null` (sin bindings), según comprobación previa. `GCP_STAGING_ENABLED=false` confirmado. Backend permanece privado; no se modificaron otras aplicaciones.

## Próxima validación: /health autenticado

Prioridad: probar una identidad IAM ya autorizada; **no conceder roles globales** ni hacer público el servicio. Ejecutar:

```bash
gcloud run services proxy smartroute-gateway-staging \
  --project=proyectopersonal-480420 \
  --region=us-central1 \
  --port=18080
```

Con el proxy abierto, en otra pestaña de Cloud Shell:

```bash
curl -i --max-time 15 http://127.0.0.1:18080/health
```

Esperado **si la identidad de usuario ya tiene roles/run.invoker sobre el gateway**: `HTTP 200` con estado `ok`; el proxy podría devolver `403` si la identidad actual no tiene invoker. En ese caso, detenerse y revisar los permisos precisos; si se requiere acceso temporal, proponer `roles/run.invoker` **sobre gateway exclusivamente** y obtener autorización del propietario. No inferir que `gcloud run services proxy` crea permisos.

Luego probar Firebase faltante/incorrecto, y flujo de credenciales Firebase válidas. `/health` por sí solo no usa Firebase ni backend.

**Invariantes:** Firestore `smartroute` solamente, no tocar `(default)` ni `gestioncitas`; no modificar proveedor Google Sign-In o configuración Firebase compartida; backend privado, gateway IAM privado hasta gate de seguridad/antiabuso.
