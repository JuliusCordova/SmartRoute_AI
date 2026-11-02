# SmartRoute GCP IAM — etapa 1: confianza WIF y base dedicada

## Recursos existentes (evidencia Cloud Shell del usuario)
- Proyecto `proyectopersonal-480420` / `913797829604`.
- Firestore Standard `smartroute`, región `nam5`, protección contra eliminación habilitada.
- Cuentas creadas `smartroute-deployer`, `smartroute-runtime`, `smartroute-smoke`.
- Pool `smartroute-ci` ACTIVE; proveedor `smartroute-main` ACTIVE, issuer `https://token.actions.githubusercontent.com`; condición **repo y rama main**, comprobada por el usuario.

## Etapa 1 (NO ejecutada por ChatGPT)
El script `scripts/gcp-bind-smartroute-iam.sh` verifica el proyecto, base, identidades y el proveedor OIDC, y actúa en dos pasos:
1. `roles/iam.workloadIdentityUser` para el principal federado `principalSet://iam.googleapis.com/projects/913797829604/locations/global/workloadIdentityPools/smartroute-ci/attribute.repository/JuliusCordova/SmartRoute_AI` sobre las cuentas **deployer** y **smoke** únicamente. El proveedor exige la rama `refs/heads/main` y la URL del issuer exacta.
2. `roles/datastore.user` a `smartroute-runtime` con IAM Condition de recurso **exacta** `resource.name=='projects/proyectopersonal-480420/databases/smartroute'`, sin conceder acceso a las otras bases por este binding.

Estos permisos **no habilitan despliegue de Cloud Run** y no incluyen token creator, serviceAccountUser, roles de Cloud Build, roles globales de Firestore, ni invocación. No modifican las bases `(default)` y `gestioncitas`. Las Condiciones IAM de Firestore aplican a las bibliotecas de servidor; **la consola GCP no refleja las mismas restricciones**. La propagación IAM puede tardar algunos minutos. <https://firebase.google.com/docs/firestore/manage-databases>

### Modo lectura / plan (sin cambios)
```bash
cd ~/SmartRoute_AI
git pull --ff-only
bash scripts/gcp-bind-smartroute-iam.sh
```

### Aplicación manual y acotada
```bash
CONFIRM_SMARTROUTE_IAM_BINDINGS=proyectopersonal-480420/smartroute \
  bash scripts/gcp-bind-smartroute-iam.sh
```

Este paso aplica vinculaciones IAM; requiere la autorización del propietario del proyecto y permisos para modificar IAM. No imprimir volcados completos de políticas ni tokens en el chat. Si falla a mitad, revisar qué permisos se crearon antes de reintentar.

## Siguiente etapa (separada y pendiente)
- Verificar bindings específicos de cada cuenta y la condición de Firestore sin divulgar la política IAM completa.
- Decidir controles de costo y cuotas de Cloud Run/Cloud Build para staging.
- Revisar los permisos de despliegue de origen: Google Cloud indica `roles/run.sourceDeveloper` y `roles/serviceusage.serviceUsageConsumer` **a nivel de proyecto**, y `roles/iam.serviceAccountUser` sobre la identidad runtime; `roles/run.builder` para la identidad build que use Cloud Build. En un proyecto compartido estas concesiones requieren un gate de aprobación separado.
- Crear servicio `smartroute-api-staging` privado, y conceder `roles/run.invoker` a smoke solamente sobre ese servicio, después de existir.
- Configurar GitHub Actions variables: `GCP_PROJECT_ID=proyectopersonal-480420`, `GCP_FIRESTORE_DATABASE_ID=smartroute`, provider completo, deployer/runtime/smoke, región. Mantener `GCP_STAGING_ENABLED=false` hasta completar la etapa.
- Resolver doble token Cloud Run IAM vs Firebase ID token para Flutter/React; un ID token de Firebase no autoriza automáticamente la invocación de un servicio Cloud Run privado.

Referencias:
- https://docs.cloud.google.com/iam/docs/workload-identity-federation
- https://firebase.google.com/docs/firestore/manage-databases
- https://docs.cloud.google.com/run/docs/deploying-source-code
