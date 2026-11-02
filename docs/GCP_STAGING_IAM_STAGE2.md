# SmartRoute — IAM etapa 2: despliegue CI/CD acotado por recurso

## Estado comprobado con ejecución del propietario
- Artifact Registry `smartroute-staging` creado en `us-central1`.
- Cloud Run privado `smartroute-api-staging` publicado con imagen de digest `sha256:ae202c8d092a02ae416cc0a2c5b246259b98946a0b2204d10376795c05591a10`, revisión `smartroute-api-staging-00001-2vt`, 100 % tráfico, runtime `smartroute-runtime`.
- `/health` y `/ready` comprobaron PASS mediante proxy local autenticado. No prueban Firebase ni consultas de datos de Firestore.
- WIF etapa 1 de `deployer` y `smoke` y permiso condicional de runtime sobre base `smartroute` también están comprobados.
- **`GCP_STAGING_ENABLED` continúa deshabilitado**; no está probado el despliegue automatizado ni los accesos reales de Firestore.

## Permisos mínimos propuestos para staging
`scripts/gcp-bind-staging-deploy-iam.sh` primero verifica identidades y recursos, que Cloud Run usa `smartroute-runtime` y que su IAM no contiene principales públicos; por defecto es simulación. Con confirmación aplica:

| Principal | Rol | Recurso, sin alcance de proyecto |
|---|---|---|
| smartroute-deployer | `roles/artifactregistry.writer` | repositorio Artifact Registry `smartroute-staging` |
| smartroute-deployer | `roles/run.developer` | servicio Cloud Run `smartroute-api-staging` |
| smartroute-deployer | `roles/iam.serviceAccountUser` | cuenta `smartroute-runtime` |
| smartroute-smoke | `roles/run.invoker` | servicio Cloud Run `smartroute-api-staging` |
| smartroute-smoke | `roles/iam.serviceAccountTokenCreator` | **su propia cuenta** solamente |

El último permiso se utiliza para generar tokens Google ID desde `google-github-actions/auth`, y **no** se otorga sobre todo el proyecto. El workflow ahora solicita `id_token_include_email: true`.

### Paso 1 — dry run
```bash
cd ~/SmartRoute_AI
git pull --ff-only
bash scripts/gcp-bind-staging-deploy-iam.sh
```

### Paso 2 — aplicación por el propietario
```bash
CONFIRM_SMARTROUTE_DEPLOY_GRANTS=proyectopersonal-480420/smartroute-api-staging \
 bash scripts/gcp-bind-staging-deploy-iam.sh
```

**No aplicar roles run.admin ni run.developer en todo el proyecto.** Si el comando falla a mitad, verificar qué vinculaciones se actualizaron antes de reintentar.

## Paso posterior: GitHub Actions
Confirmar en settings del repositorio la presencia de `staging` Environment y variables:
- `GCP_PROJECT_ID=proyectopersonal-480420`
- `GCP_REGION=us-central1`
- `GCP_FIRESTORE_DATABASE_ID=smartroute`
- `GCP_WIF_PROVIDER=projects/913797829604/locations/global/workloadIdentityPools/smartroute-ci/providers/smartroute-main`
- `GCP_DEPLOYER_SERVICE_ACCOUNT=smartroute-deployer@proyectopersonal-480420.iam.gserviceaccount.com`
- `GCP_RUNTIME_SERVICE_ACCOUNT=smartroute-runtime@proyectopersonal-480420.iam.gserviceaccount.com`
- `GCP_SMOKE_SERVICE_ACCOUNT=smartroute-smoke@proyectopersonal-480420.iam.gserviceaccount.com`

Las variables de entorno de GitHub se evalúan con `vars.*`; si se configuran solo en `staging` Environment, las condiciones del job deben considerar su alcance. **Conservar `GCP_STAGING_ENABLED=false`/ausente** hasta probar el acceso WIF, que el pipeline publique el digest, y la seguridad del smoke. Pruebas finales incluyen Firebase Auth y Firestore real.

## Referencias
- https://docs.cloud.google.com/run/docs/reference/iam/roles
- https://docs.cloud.google.com/artifact-registry/docs/access-control
- https://github.com/google-github-actions/auth#generating-id-tokens
