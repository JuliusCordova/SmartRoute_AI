# Etapa 1 IAM — verificación de solo lectura

El propietario ejecutó satisfactoriamente `scripts/gcp-bind-smartroute-iam.sh`. La salida mostró:
- `roles/iam.workloadIdentityUser` en las cuentas **smartroute-deployer** y **smartroute-smoke** para el principal federado del repositorio SmartRoute.
- `roles/datastore.user` para `smartroute-runtime` con la condición exacta `resource.name=='projects/proyectopersonal-480420/databases/smartroute'`.
- `IAM STAGE 1 COMPLETE`. No se concedieron por ese procedimiento roles de Cloud Run, Cloud Build ni accesos sobre las bases ajenas.

Para verificar sin exponer la política IAM de terceros:
```bash
cd ~/SmartRoute_AI
git pull --ff-only
bash scripts/gcp-verify-smartroute-iam.sh
```

La comprobación no cambia permisos, imprime únicamente PASS/FAIL, y detecta si el runtime tiene también vinculaciones `roles/datastore.user` **sin la condición exacta** directamente en el proyecto. No comprueba roles heredados, otros roles capaces de leer Firestore, ni permisos efectivos de Cloud Run. Una prueba de acceso real a la base se requiere antes de habilitar staging.

**Próximo gate:** evaluar permisos de despliegue de alcance proyecto, cuentas Cloud Build y GitHub Actions Environment, con `GCP_STAGING_ENABLED=false`. Proteger cuentas y datos del proyecto compartido y evitar volcar políticas IAM completas en el chat.
