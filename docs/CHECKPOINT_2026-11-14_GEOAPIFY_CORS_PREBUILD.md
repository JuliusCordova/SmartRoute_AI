# Checkpoint de evidencia — Geoapify, CORS y preparación del backend

**Fecha de registro:** 2026-11-14, zona America/Lima (salidas de Cloud Run con fecha UTC 2026-11-15).  
**Proyecto:** SmartRoute AI — Capstone UPN, web-first.  
**Repositorio:** https://github.com/JuliusCordova/SmartRoute_AI  
**Rama:** `feat/operator-web-osm-routing-pilot`  
**PR:** https://github.com/JuliusCordova/SmartRoute_AI/pull/53  
**Checkpoint anterior:** [CHECKPOINT_2026-11-14_WEB_OPERATOR_GEOCODING.md](./CHECKPOINT_2026-11-14_WEB_OPERATOR_GEOCODING.md)

> **Estado al cerrar esta evidencia:** frontend actual operativo y login Google confirmado por el usuario; CORS corregido y verificado; clave Geoapify registrada de forma segura como secreto y conectada a Cloud Run. **El nuevo código de autocompletado del PR todavía NO está desplegado.** El build indicado como paso 58 **no se ha ejecutado**. No se hizo merge ni se modificaron otros proyectos.

## 1. Propósito y alcance

El objetivo UX del operador es **buscar una dirección → seleccionar una sugerencia → obtener coordenadas automáticamente → mostrar marcador en OpenStreetMap → validar advertencias de precisión → guardar pedido ficticio en Firestore `smartroute`**. Ya existe implementación de frontend y backend en la rama del PR, pero falta llevarla a staging y hacer una prueba E2E. La optimización OR-Tools/openrouteservice está implementada como previsualización no persistente y su prueba contra proveedor real sigue pendiente.

El proyecto GCP `proyectopersonal-480420`, región `us-central1`, está compartido con otras aplicaciones. **No tocar** servicios ajenos, secretos ajenos ni las bases Firestore `(default)` y `gestioncitas`.

## 2. Evidencia de sincronización, CI y Cloud Shell

Comando ejecutado por el usuario:

```bash
cd ~/SmartRoute_AI && git status -sb && git pull --ff-only && git log -1 --oneline
```

Resultado comprobado en la salida:

```text
## feat/operator-web-osm-routing-pilot...origin/feat/operator-web-osm-routing-pilot
?? services/api/.venv/
Updating dcd42aa..d4410b1
Fast-forward
d4410b1 (HEAD -> feat/operator-web-osm-routing-pilot, origin/feat/operator-web-osm-routing-pilot)
```

- `services/api/.venv/` es local, quedó tras instalación fallida; no versionarlo.
- Cloud Shell recuperó espacio moviendo dos directorios de estado de Code OSS a `/tmp/cloudshell-codeoss-backup/`. Lectura: `/home` de 4.8 GB, 3.7 GB usados, **940 MB disponibles (80%)**. No se eliminaron recursos de otros servicios.
- Antes pip falló con `OSError: [Errno 28] No space left on device`. No se requiere instalar OR-Tools localmente para continuar: preferir GitHub Actions y Cloud Build.
- GitHub Actions run [43562875525](https://github.com/JuliusCordova/SmartRoute_AI/actions/runs/43562875525) para checkpoint anterior: `api-tests` SUCCESS, `firestore-emulator` SUCCESS, `operator-web-build` SUCCESS y `deploy-staging` SKIPPED por diseño. **Este run no prueba una nueva imagen desplegada.**

## 3. Evidencia CORS del gateway

### Antes del cambio

Preflight browser-origin al gateway:

```bash
curl -i -X OPTIONS \
  'https://smartroute-gateway-staging-913797829604.us-central1.run.app/api/v1/orders' \
  -H 'Origin: https://smartroute-web-staging-913797829604.us-central1.run.app' \
  -H 'Access-Control-Request-Method: GET' \
  -H 'Access-Control-Request-Headers: authorization'
```

Resultado anterior: `HTTP/2 403` con `{"detail":"CORS preflight not allowed"}`.

### Cambio aplicado

La sintaxis inicial de `--update-env-vars` con coma escapada falló (no hubo despliegue). Se corrigió usando delimitador `^@^`:

```bash
gcloud run services update smartroute-gateway-staging \
  --project=proyectopersonal-480420 \
  --region=us-central1 \
  '--update-env-vars=^@^SMARTROUTE_ALLOWED_ORIGINS=http://localhost:8080,https://smartroute-web-staging-913797829604.us-central1.run.app'
```

Salida: `smartroute-gateway-staging-00003-vqm` desplegado, **100% del tráfico**.

### Después del cambio

Se repitió el preflight; salida aportada:

```http
HTTP/2 204
access-control-allow-origin: https://smartroute-web-staging-913797829604.us-central1.run.app
access-control-allow-methods: GET
access-control-allow-headers: Authorization, Content-Type
access-control-max-age: 300
vary: Origin
```

**Conclusión respaldada:** el CORS de preflight para `GET /api/v1/orders` desde el dominio web funciona. **No equivale a demostrar POST/GET con Bearer válido ni persistencia en Firestore**.

## 4. Evidencia Geoapify y Secret Manager

Usuario confirmó cuenta en **Geoapify** (no Apify) y existencia de API key. Por seguridad, **el valor de la clave NO se registra en GitHub ni en este documento**.

1. Se creó el secreto:
   ```bash
   gcloud secrets create smartroute-geoapify-api-key \
     --project=proyectopersonal-480420 --replication-policy=automatic
   ```
   Resultado: `Created secret [smartroute-geoapify-api-key]`.
2. El usuario insertó la API key con `read -r -s` y la transmitió por stdin a Secret Manager (`gcloud secrets versions add ... --data-file=-`). Resultado: `Created version [1]`.
3. Cuenta runtime API consultada, resultado:
   ```text
   smartroute-runtime@proyectopersonal-480420.iam.gserviceaccount.com
   ```
4. Se aplicó autorización **acotada al secreto**:
   ```bash
   gcloud secrets add-iam-policy-binding smartroute-geoapify-api-key \
     --project=proyectopersonal-480420 \
     --member='serviceAccount:smartroute-runtime@proyectopersonal-480420.iam.gserviceaccount.com' \
     --role='roles/secretmanager.secretAccessor'
   ```
   Resultado: `Updated IAM policy for secret [smartroute-geoapify-api-key]`, binding de `roles/secretmanager.secretAccessor` con esa cuenta.
5. Se conectó el secreto **sin publicar todavía el nuevo código**:
   ```bash
   gcloud run services update smartroute-api-staging \
     --project=proyectopersonal-480420 --region=us-central1 \
     --update-secrets=GEOAPIFY_API_KEY=smartroute-geoapify-api-key:1
   ```
   Resultado: `smartroute-api-staging-00003-qm9` desplegado, **100% del tráfico**.

### Configuración del runtime API comprobada por `gcloud run services describe`

```yaml
spec:
  template:
    spec:
      containers:
      - env:
        - name: APP_ENV
          value: staging
        - name: FIREBASE_PROJECT_ID
          value: proyectopersonal-480420
        - name: GOOGLE_CLOUD_PROJECT
          value: proyectopersonal-480420
        - name: FIRESTORE_DATABASE_ID
          value: smartroute
        - name: GEOAPIFY_API_KEY
          valueFrom:
            secretKeyRef:
              key: '1'
              name: smartroute-geoapify-api-key
      serviceAccountName: smartroute-runtime@proyectopersonal-480420.iam.gserviceaccount.com
```

No se verificó explícitamente una llamada a Geoapify desde el proceso ni se mostraron valores de secretos.

## 5. Imagen backend activa y reversión

Consulta de solo lectura:

```bash
gcloud run services describe smartroute-api-staging \
  --project=proyectopersonal-480420 --region=us-central1 \
  --format='value(spec.template.spec.containers[0].image)'
```

**Resultado comprobado (imagen ejecutada por la revisión con secreto):**

```text
us-central1-docker.pkg.dev/proyectopersonal-480420/smartroute-staging/smartroute-api@sha256:c2070587a69fceea08d81ec1d85bbbf04e9f4ea5cf5ae90355c93fd6797783a0
```

Guardar este digest como referencia de imagen anterior. Si se requiere reversión, preferir tráfico por revisión o despliegue controlado preservando variables, secretos e IAM; no asumir que fijar solo la imagen restaura toda la configuración.

Otros servicios registrados:
- Frontend `smartroute-web-staging`: revisión `00001-zbk`, URL `https://smartroute-web-staging-913797829604.us-central1.run.app`; `GET /health` = 200 en validación anterior y Google Sign-In confirmado por el usuario.
- Gateway `smartroute-gateway-staging`: revisión `00003-vqm`, URL `https://smartroute-gateway-staging-913797829604.us-central1.run.app`, nuevo CORS comprobado.
- API privada `smartroute-api-staging`: revisión `00003-qm9`, `GEOAPIFY_API_KEY` desde Secret Manager; **código nuevo pendiente**.

## 6. Código listo, evidencia faltante y próximo paso

En el PR #53 están:
- `services/api/app/geocoding.py` + ruta `GET /api/v1/geocoding/autocomplete`, protegida por `require_operator`;
- `services/gateway/app/main.py` con allowlist para geocoding;
- `apps/operator-web/src/main.jsx` con búsqueda y autocompletado, latitud/longitud automáticas, punto provisional y confirmación ante coincidencia aproximada;
- `services/api/app/route_preview.py`: previsualización OR-Tools + openrouteservice; **requiere `ORS_API_KEY` distinta, pendiente**.

**No ejecutado todavía:** paso 58 (Cloud Build del código nuevo), publicación de imagen nueva, actualización de Cloud Run API/gateway/web, prueba E2E de geocodificación, alta/lectura de pedidos y optimización real. No marcar como terminadas.

### Acción siguiente recomendada, con control

1. Comprobar que el árbol local está en la rama prevista y usar Dockerfile desde `services/api` para construir solo el backend sin enviar `.venv` a Cloud Build.
2. Ejecutar Cloud Build **solo para generar una nueva imagen**, sin modificar la revisión activa; registrar etiqueta, digest y estado.
3. Desplegar `smartroute-api-staging` usando **imagen inmutable** y conservar `FIRESTORE_DATABASE_ID=smartroute`, SA `smartroute-runtime`, secreto `GEOAPIFY_API_KEY`, IAM privado y demás variables.
4. Repetir pruebas negativas 401 sin token; confirmar nueva ruta protegida; actualizar gateway manteniendo su CORS y luego web.
5. E2E desde navegador: login Google OPERATOR, búsqueda dirección y sugerencia, validación precisa/aproximada, guardar pedido ficticio, consultar Firestore `smartroute`. Posteriormente ORS/OR-Tools.

**Seguridad:** jamás imprimir/API keys, JWT de Firebase, credenciales ni valores secretos en logs/commits; el frontend no recibe `GEOAPIFY_API_KEY`; mantener protección de bases y servicios ajenos.

---
Esta evidencia se basa en salidas de Cloud Shell compartidas durante el desarrollo y en el código/CI revisado en GitHub. Describe resultados observados y distingue actividades pendientes; no constituye certificación de pruebas E2E.
