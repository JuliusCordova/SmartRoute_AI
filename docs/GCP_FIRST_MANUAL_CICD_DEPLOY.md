# Primer despliegue completo desde GitHub — control manual

## Estado de protección validado por Cloud Shell
- Rama `main` protegida con required checks `api-tests`, `firestore-emulator` en modo strict; force push y borrados desactivados.
- Entorno GitHub `staging` creado, permitido solo desde ramas protegidas.
- GitHub Actions variables (8) configuradas. `GCP_STAGING_ENABLED=false`.
- WIF manual `verify-wif-private-smoke`: éxito.
- Cloud Run privado `smartroute-api-staging` operativo y `/health`, `/ready` probados.
- IAM etapa 2: cinco vinculaciones sobre recursos de SmartRoute verificadas mediante script.

## Nuevo workflow, independiente del despliegue continuo
`.github/workflows/manual-staging-deploy.yml` ejecuta únicamente `workflow_dispatch` en `main`, con `environment: staging` y variables ancladas a los valores esperados. Se rehúsa a correr si `GCP_STAGING_ENABLED` no es `false`.

1. WIF deployer (sin claves JSON).
2. Verifica que Cloud Run y Artifact Registry exclusivos existan y el runtime sea `smartroute-runtime`.
3. Compila Docker, publica imagen en repositorio SmartRoute y extrae digest inmutable.
4. Despliega **únicamente** `smartroute-api-staging`, sin cambiar identidad runtime, base Firestore o límites 0-2 instancias.
5. WIF smoke + token de audiencia restringida; comprueba `/health` y `/ready`.
6. Registra commit/digest y resultado en GitHub Actions Summary.

## Ejecución manual por el propietario
Abrir:
https://github.com/JuliusCordova/SmartRoute_AI/actions/workflows/manual-staging-deploy.yml

Seleccionar `Run workflow`, rama `main`. Es un despliegue **real** que puede tener costos de almacenamiento, red y cómputo. No es una simulación ni activa el CI/CD continuo.

No correr ante cambios pendientes de CI, entorno inseguro o desajustes de variables. Si falla, revisar solamente el paso específico de GitHub Actions; evitar permisos amplios o apertura pública de Cloud Run como solución rápida.

## Límites de la evidencia
Una ejecución exitosa valida WIF, publicación de imagen, actualización de revisión Cloud Run y endpoints de salud, pero **no** autenticación Firebase, lectura/escritura en Firestore ni flujo Android/React. No activar automáticamente `GCP_STAGING_ENABLED=true` sin revisar costos/alertas, experiencia de clientes y condiciones de rollback.
