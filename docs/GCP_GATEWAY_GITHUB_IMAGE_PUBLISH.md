# Recuperación de Artifact Registry con GitHub Actions (sin Docker push en Cloud Shell)

## Situación confirmada
- Cloud Shell `docker build` correcto, pero cuatro intentos `docker push` a `us-central1-docker.pkg.dev:443` fallaron con `connect: connection refused`.
- `gcloud run deploy` no se ejecutó; no se ha confirmado creación de `smartroute-gateway-staging`.
- IAM del backend privado y grant `smartroute-gateway -> roles/run.invoker` exclusivo PASARON.
- El flujo de WIF de GitHub ya demostró publicar una imagen del backend en el mismo repositorio de Artifact Registry.

## Alternativa aislada: publicación manual GitHub

Se añadió `.github/workflows/manual-gateway-image-publish.yml`:
- Solo se ejecuta vía `workflow_dispatch` desde `main`, en entorno GitHub `staging` limitado a ramas protegidas.
- Verifica proyecto, región, WIF y deployer exactos.
- Reutiliza WIF y la cuenta `smartroute-deployer`, cuyo writer está acotado al repositorio `smartroute-staging`.
- Construye `services/gateway/` y publica la imagen `smartroute-gateway:<commit SHA>` en el repositorio SmartRoute.
- Devuelve el URI **por digest SHA256** en el resumen del job.
- **No despliega Cloud Run, no cambia IAM, no habilita entrada pública, no modifica Firebase/Firestore y no cambia `GCP_STAGING_ENABLED=false`.**
- GitHub-hosted build y almacenamiento de imagen pueden generar costos; no se activa ejecución recurrente.

### 1. Ejecución manual
En GitHub → Actions → **SmartRoute gateway image publish (manual only)** → Run workflow → rama `main`. O bien, desde Cloud Shell:
```bash
gh workflow run manual-gateway-image-publish.yml --ref main --repo JuliusCordova/SmartRoute_AI
gh run list --workflow manual-gateway-image-publish.yml --repo JuliusCordova/SmartRoute_AI --limit 3
```

Revisar el log y el resumen de ejecución hasta obtener URI:
`us-central1-docker.pkg.dev/proyectopersonal-480420/smartroute-staging/smartroute-gateway@sha256:<64 caracteres>`.

### 2. No desplegar inmediatamente sin validación
Verificar que la ejecución terminó `success`, el digest pertenece al repositorio exclusivo y que `smartroute-gateway-staging` sigue sin existir. Después preparar un bootstrap privado que acepte únicamente URI digest validado y mantenga los controles IAM previos. No reutilizar el script que reconstruye Docker en Cloud Shell porque volverá a enfrentar el problema de red.

### 3. Límites
No modificar los servicios de otras aplicaciones; el proyecto es compartido. La imagen publicada no convierte al gateway en público. Aún quedan pendientes el primer despliegue privado, pruebas IAM/Firebase, usuario OPERATOR, antiabuso y acceso Android/web.
