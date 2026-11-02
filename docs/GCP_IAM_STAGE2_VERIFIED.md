# Verificación de IAM — CI/CD SmartRoute etapa 2

## Evidencia proporcionada por el operador
El 2 de noviembre de 2026 se ejecutó con éxito `CONFIRM_SMARTROUTE_DEPLOY_GRANTS=proyectopersonal-480420/smartroute-api-staging bash scripts/gcp-bind-staging-deploy-iam.sh`. Los cinco comandos de vinculación IAM reportaron `Updated IAM policy` y el script finalizó con `IAM STAGE 2 COMPLETE`.

## Revalidar sin exponer políticas ajenas
```bash
cd ~/SmartRoute_AI
git pull --ff-only
bash scripts/gcp-verify-staging-deploy-iam.sh
```

El verificador obtiene políticas de **repositorio**, **servicio** y **cuentas de servicio** exclusivamente de SmartRoute. Solo imprime PASS/FAIL, no vuelca las políticas en la terminal, y verifica:
- deployer + `roles/artifactregistry.writer` en `smartroute-staging`;
- deployer + `roles/run.developer` en `smartroute-api-staging`;
- deployer + `roles/iam.serviceAccountUser` en `smartroute-runtime`;
- smoke + `roles/run.invoker` en `smartroute-api-staging`;
- smoke + `roles/iam.serviceAccountTokenCreator` en su propia cuenta;
- que el servicio no tenga bindings públicos `allUsers` / `allAuthenticatedUsers`.

Esta verificación es solo de política directa, no evalúa permisos heredados o efectiva ejecución WIF/Cloud Run.

## Paso posterior
Tras PASS, comprobar GitHub Actions repo variables y environment `staging`. El workflow usa `vars.GCP_STAGING_ENABLED == 'true'` en la condición del job, así que el flag debe estar a nivel de repositorio (no basta configurarlo únicamente a nivel de Environment). La habilitación queda separada de esta verificación.

Mantener staging desactivado hasta asegurar rama protegida, cuentas correctas, pruebas WIF, y pruebas del flujo Firebase/Firestore; revisar costos y alertas del proyecto compartido.
