# Cloud Run staging — preflight de despliegue

## Estado validado por el usuario (IAM etapa 1)
La salida de `scripts/gcp-verify-smartroute-iam.sh` confirma:
- PASS para el vínculo WIF de `smartroute-deployer`.
- PASS para el vínculo WIF de `smartroute-smoke`.
- PASS para el permiso de `smartroute-runtime` condicionado a la base exacta `smartroute`.
- PASS general de verificaciones de IAM etapa 1, **sin cambios en GCP durante esa verificación**.

Estos checks verifican las vinculaciones IAM, pero no una consulta de datos efectiva ni privilegios heredados de otras cuentas.

## Próxima ejecución segura
```bash
cd ~/SmartRoute_AI
git pull --ff-only
SMARTROUTE_REGION=us-central1 bash scripts/gcp-cloudrun-readiness.sh
```
Solo lee APIs habilitadas, identidades y nombres de servicios. No muestra IAM de terceros ni modifica Cloud Run.

## Gate de seguridad para habilitar staging
El proyecto está **compartido con Atlas DataGob, Gestión de Citas y otros servicios**. Por ello no se concederán aún roles de despliegue. Según la documentación de Cloud Run para source deploy, el deployer normalmente necesita `roles/run.sourceDeveloper` y `roles/serviceusage.serviceUsageConsumer` sobre el proyecto, y `roles/iam.serviceAccountUser` sobre la cuenta de ejecución; Cloud Build necesita `roles/run.builder` sobre la cuenta real del build. Los primeros dos roles cubren el proyecto completo, por lo que requieren aceptación explícita del riesgo o una alternativa más granular con imágenes/roles personalizados.

Después de comprobar la identidad real de Cloud Build, escoger despliegue desde código vs imagen. Si se opta por el flujo directo source-deploy con permisos amplios, documentar exactamente su alcance. Revisar presupuesto de facturación y alarmas (no son topes duros).

Además, el pipeline actual usa una autenticación de Cloud Run IAM en `smoke-test.sh`, mientras que endpoints de negocio esperan un Firebase ID token. Es un doble control; no habilitar acceso Android/React sin diseñar gateway/proxy de autenticación. El staging está **desactivado** y no existe servicio SmartRoute.

Fuentes:
- https://docs.cloud.google.com/run/docs/deploying-source-code
- https://docs.cloud.google.com/run/docs/reference/iam/roles
- https://docs.cloud.google.com/run/docs/configuring/services/build-service-account
