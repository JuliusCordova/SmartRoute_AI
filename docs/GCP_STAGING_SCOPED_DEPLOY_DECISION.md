# SmartRoute AI — decisión de despliegue staging en proyecto GCP compartido

## Evidencia GCP confirmada por el usuario
- Proyecto `proyectopersonal-480420` / número `913797829604`.
- APIs habilitadas: Artifact Registry, Cloud Build, Firestore, IAM Credentials, Cloud Run y STS.
- Cuenta real por defecto de Cloud Build: `913797829604-compute@developer.gserviceaccount.com`.
- Cuentas separadas `smartroute-deployer`, `smartroute-runtime`, `smartroute-smoke` existentes.
- Sin colisión con servicio Cloud Run `smartroute-api-staging` en `us-central1`.
- IAM etapa 1 verificada PASS, incluyendo condición exacta sobre `smartroute`.

## Decisión recomendada: no otorgar Cloud Run Source Developer al CI
En un proyecto que ya aloja Atlas DataGob, Prima, Ayni y otros servicios, **NO** conceder `roles/run.sourceDeveloper`, `roles/run.developer` o `roles/run.admin` de alcance global al principal de GitHub. El método actual de `.github/workflows/ci.yml` utiliza `deploy-cloudrun@v3` con `source: services/api` y exigiría permisos de source deploy sobre el proyecto; por tanto **no debe habilitarse todavía**.

### Diseño alternativo de mínimo privilegio
1. **Bootstrap de una sola vez con el propietario:** preparar Artifact Registry Docker repo exclusivo `smartroute-staging` en `us-central1` y un servicio privado Cloud Run `smartroute-api-staging` creado con identidad `smartroute-runtime` y variable `FIRESTORE_DATABASE_ID=smartroute`. Requiere autorización separada de recursos facturables y revisión de IAM; no ejecutado.
2. **Build de imagen:** usar GitHub Actions Docker build, luego push al repositorio Artifact Registry dedicado. Conceder `roles/artifactregistry.writer` al deployer **solo sobre el repositorio dedicado**, no en el proyecto entero. Evitar que la cuenta Compute predeterminada construya imágenes de SmartRoute si se puede construir en GitHub.
3. **Deploy solo de revisiones:** sustituir el campo `source` del workflow por una referencia de imagen inmutable `@sha256:`, y conceder `roles/run.developer` a deployer solo sobre el servicio SmartRoute existente, además de `roles/iam.serviceAccountUser` solo sobre `smartroute-runtime`. Para leer imágenes, conceder al principal que lo necesite `roles/artifactregistry.reader` sobre el repositorio dedicado. **Comprobar en Cloud Run las operaciones permitidas de cada identidad antes de habilitar CI**.
4. **Smoke:** asignar `roles/run.invoker` a `smartroute-smoke` solo sobre `smartroute-api-staging`; validar la generación de ID tokens por WIF sin conceder el rol Token Creator a nivel proyecto.
5. **Seguridad:** Cloud Run privado, `min-instances=0`, límites de instancias y CPU/memoria acordes con piloto, presupuestos de alerta; mantener `GCP_STAGING_ENABLED=false` hasta verificar WIF, artefactos, endpoint y autenticación Firebase. El doble token Cloud Run IAM / Firebase requiere una solución de gateway o backend-for-frontend antes de usar la app móvil.

## Riesgos y gates
- **Permisos para crear el servicio** requieren alcance del proyecto: la creación inicial la realizará el propietario con sus privilegios administrativos actuales, no la identidad CI.
- **Factura:** Artifact Registry, Cloud Run y tráfico pueden producir cargos. Presupuestos y alertas no constituyen límites estrictos de gasto.
- **Cambio pendiente del pipeline:** no activar el workflow actual en su modo `source`; todavía **NO se ha convertido** a build/push/deploy por digest.
- **Validación de seguridad:** revisiones de GitHub Actions en rama main podrían ejecutar código de los colaboradores que tengan capacidad de merge; mantener branch protections/environment protections.
- **Estado:** este documento es solo una decisión arquitectónica; no se han creado nuevos recursos GCP.

## Referencias oficiales
- https://docs.cloud.google.com/run/docs/reference/iam/roles
- https://docs.cloud.google.com/run/docs/deploying-source-code
- https://docs.cloud.google.com/run/docs/securing/managing-access
- https://docs.cloud.google.com/artifact-registry/docs/access-control
