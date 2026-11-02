# Staging autorizado: Artifact Registry + Cloud Run privado

## Autorización del propietario
El usuario aprobó explícitamente crear en `proyectopersonal-480420`:
1. Repositorio Docker `smartroute-staging` en `us-central1`.
2. Servicio privado Cloud Run `smartroute-api-staging` en `us-central1`, `min-instances=0`, `max-instances=2`, 1 vCPU, 512 MiB RAM, concurrencia 10, timeout 30 segundos.

La autorización **no** comprende acceso público, eliminación de recursos, permisos IAM de proyecto amplios, activación automática del CI/CD ni costos ilimitados. Las bases Firestore `(default)` y `gestioncitas` se preservan. Base propia `smartroute` Standard/Native, protección habilitada.

## Bootstrap propietario en Cloud Shell
El script `scripts/gcp-bootstrap-staging-service.sh` muestra un plan sin cambios por defecto. Para ejecutarlo:
```bash
cd ~/SmartRoute_AI
git pull --ff-only
bash scripts/gcp-bootstrap-staging-service.sh
CONFIRM_SMARTROUTE_STAGING_BOOTSTRAP=proyectopersonal-480420/smartroute-api-staging \
  bash scripts/gcp-bootstrap-staging-service.sh
```

La creación realiza: repositorio Docker dedicado, `docker build` de FastAPI desde `services/api`, push de imagen etiquetada por commit, y despliegue inicial **privado** de servicio existente con `smartroute-runtime`. No otorga privilegios IAM a GitHub y no activa `GCP_STAGING_ENABLED`. Una falla después de crear el repositorio podría dejarlo creado pero sin servicio; repetir el script solo después de revisar el estado. Una ejecución posterior exitosa se bloquea si el servicio ya existe, para evitar despliegues accidentales.

**Cloud Shell debe disponer de Docker** y de permiso de crear repositorio Artifact Registry y Cloud Run; si faltan permisos, NO conceder permisos genéricos al deployer. El propio usuario ejecuta este bootstrap con sus privilegios de propietario.

## Pipeline GitHub Actions preparado pero desactivado
El workflow dejó de usar `source: services/api` y utiliza:
1. GitHub WIF de `smartroute-deployer`.
2. `docker build` y push de imagen a Artifact Registry `smartroute-staging`.
3. Captura de digest `sha256` de la imagen publicada.
4. `deploy-cloudrun@v3` al servicio preexistente mediante digest inmutable.
5. Smoke IAM con `smartroute-smoke`.

Configurar solo después de grant mínimos:
- Deployer: `roles/artifactregistry.writer` en repositorio `smartroute-staging` y `roles/run.developer` en servicio `smartroute-api-staging`.
- Deployer: `roles/iam.serviceAccountUser` solamente en `smartroute-runtime`.
- Smoke: `roles/run.invoker` únicamente en `smartroute-api-staging`, y validar generación del ID token de servicio por WIF.
- Artifact Registry reader cuando el despliegue lo necesite, limitando el alcance al repositorio.
- Configuración repo/environment: `GCP_PROJECT_ID=proyectopersonal-480420`, `GCP_REGION=us-central1`, `GCP_FIRESTORE_DATABASE_ID=smartroute`, `GCP_WIF_PROVIDER=projects/913797829604/locations/global/workloadIdentityPools/smartroute-ci/providers/smartroute-main`; cuentas deployer/runtime/smoke completas.
- Mantener `GCP_STAGING_ENABLED=false` hasta permisos y smoke listos.

**Precauciones:** Cloud Run y Artifact Registry pueden generar costos; la configuración `max-instances=2` no representa un tope monetario. Recomendable configurar alertas presupuestarias en la cuenta de facturación. No se ha comprobado el acceso en vivo a Firestore; la autenticación Firebase cliente y Cloud Run privado siguen siendo capas separadas.

## Referencias oficiales
- https://docs.cloud.google.com/sdk/gcloud/reference/run/deploy
- https://docs.cloud.google.com/sdk/gcloud/reference/artifacts/repositories/create
- https://docs.cloud.google.com/run/docs/reference/iam/roles
