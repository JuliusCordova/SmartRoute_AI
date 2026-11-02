# Gate previo a automatizar SmartRoute: WIF manual

El usuario ejecutó `scripts/gcp-verify-staging-deploy-iam.sh` en Cloud Shell. Resultado: **PASS en las cinco vinculaciones IAM** y **PASS para ausencia de principals públicos en Cloud Run**.

## Prueba manual controlada desde GitHub Actions
Workflow: `.github/workflows/wif-staging-preflight.yml`

Sólo corre mediante `workflow_dispatch` en la rama `main` del repositorio `JuliusCordova/SmartRoute_AI`. No depende de variables GitHub, no publica imágenes, no crea revisiones, no modifica Firestore ni IAM. Comprueba:
1. WIF de `smartroute-deployer` e inspección de metadatos de su repositorio y servicio exclusivos.
2. WIF de `smartroute-smoke`, emisión de ID token restringido a audiencia de `smartroute-api-staging` e inclusión del email.
3. Respuesta `/health` y `/ready` del servicio Cloud Run privado mediante token de smoke.

### Ejecutar desde la interfaz GitHub
Abrir `https://github.com/JuliusCordova/SmartRoute_AI/actions/workflows/wif-staging-preflight.yml`, escoger **Run workflow**, rama **main** y confirmar. Alternativamente, con GitHub CLI autenticado:
```bash
gh workflow run wif-staging-preflight.yml -R JuliusCordova/SmartRoute_AI --ref main
gh run list -R JuliusCordova/SmartRoute_AI --workflow wif-staging-preflight.yml --limit 3
```

Ante un error, revisar el paso concreto del run, **sin otorgar roles de administrador globales**. El endpoint es privado, no se registra el token en logs. Los smoke sólo prueban la salud del proceso, no persistencia Firestore ni login Firebase.

## Habilitación automática (separada)
La etapa siguiente consiste en definir variables GitHub Actions para el workflow `ci.yml` y probar despliegue por digest. **Mantener `GCP_STAGING_ENABLED=false` o ausente** hasta validar el WIF manual y revisar ambiente protegido `staging`, rama main, la política de acceso de los clientes y facturación/alertas.
