# SmartRoute AI — identidad dedicada GCP y WIF

## Preflight completado (aportado por el usuario)
- Firestore `smartroute`: STANDARD / FIRESTORE_NATIVE / nam5 / delete protection enabled / freeTier false.
- No hay cuentas de servicio llamadas `smartroute-*`.
- No existe pool `smartroute-ci` identificado. Otros cinco pools WIF pertenecen a otros trabajos y **no deben modificarse**.
- No existe Cloud Run `smartroute-api-staging`.

## Alcance del script de bootstrap
El script `scripts/gcp-bootstrap-smartroute-identities.sh` crea únicamente tres cuentas de servicio nuevas y un pool/proveedor WIF exclusivos, condicionado a confirmación:
- `smartroute-deployer@proyectopersonal-480420.iam.gserviceaccount.com`
- `smartroute-runtime@proyectopersonal-480420.iam.gserviceaccount.com`
- `smartroute-smoke@proyectopersonal-480420.iam.gserviceaccount.com`
- `projects/913797829604/locations/global/workloadIdentityPools/smartroute-ci/providers/smartroute-main`

El proveedor OIDC aplica simultáneamente `assertion.repository == 'JuliusCordova/SmartRoute_AI'` y `assertion.ref == 'refs/heads/main'`. No se utiliza una clave JSON. **El script no configura permisos sobre datos ni despliegue, no toca pools existentes, no habilita staging, y se detiene ante un pool con el mismo nombre ya existente.** Si falta permiso para inspeccionar recursos, revisar los errores manualmente antes de continuar.

## Ejecución manual en Cloud Shell
```bash
cd ~/SmartRoute_AI
git pull --ff-only
bash scripts/gcp-bootstrap-smartroute-identities.sh  # dry run
CONFIRM_SMARTROUTE_IDENTITY_SETUP=proyectopersonal-480420/smartroute-ci \
  bash scripts/gcp-bootstrap-smartroute-identities.sh
```

**Precaución:** crea recursos IAM de larga duración en el proyecto existente y establece una relación de confianza con GitHub, aunque por sí solo no concede acceso a datos/Cloud Run. Revisar administración de identidades y auditoría del proyecto antes de ejecutar.

## Gate siguiente: privilegios IAM
Separar cambios y verificarlos antes de aplicar:
1. WIF `roles/iam.workloadIdentityUser` sobre las cuentas deployer y smoke, vinculado al pool exclusivo. La condición del proveedor restringe GitHub a `main`. Evaluar endurecer por `repository_id` inmutable.
2. Runtime `roles/datastore.user` **solo** condicionado al recurso `projects/proyectopersonal-480420/databases/smartroute`. Nunca conceder Datastore User sin condición sobre este proyecto compartido.
3. Deployer permisos mínimos de Cloud Run *source deploy*. Según documentación puede requerir `roles/run.sourceDeveloper`, `roles/serviceusage.serviceUsageConsumer` a nivel de proyecto, `roles/iam.serviceAccountUser` únicamente sobre `smartroute-runtime`, y `roles/run.builder` para la identidad real de Cloud Build. **Son permisos amplios en un proyecto compartido; requieren revisión especial.** Considerar despliegue desde imagen preconstruida para reducir alcance.
4. Smoke necesita `roles/run.invoker` únicamente sobre `smartroute-api-staging` y, para generar ID token, revisar `roles/iam.serviceAccountTokenCreator` sobre sí misma y opciones de federación. No conceder invoker en todo el proyecto.
5. El workflow ya exige variables GCP. Agregar `GCP_FIRESTORE_DATABASE_ID=smartroute`, conservar `GCP_STAGING_ENABLED=false`.
6. Cloud Run privado con Firebase Auth presenta **doble autenticación**: el token IAM de invocación no equivale a Firebase ID token de usuario. Resolver diseño de cliente/API Gateway antes de afirmar app Android E2E.

## Estado
El código/plan permite hacer el bootstrap, **pero el asistente no tiene acceso directo a GCP**. Si hay permisos insuficientes o errores, no aplicar permisos indiscriminados.

Fuentes:
- https://github.com/google-github-actions/auth
- https://docs.cloud.google.com/run/docs/deploying-source-code
- https://firebase.google.com/docs/firestore/manage-databases
