# Incidente IAM etapa 2: error de formato tras primera vinculación

## Evidencia de Cloud Shell (2026-11-02)
El usuario ejecutó `scripts/gcp-bind-staging-deploy-iam.sh` con autorización. La salida:
```text
Updated IAM policy for repository [smartroute-staging].
ERROR: ... Format [value] requires a non-empty projection.
```
El comando de Artifact Registry reportó **haber actualizado la política**, pero la CLI devolvió un error al intentar representar la salida con `--format='value()'`. Debido a `set -e`, las siguientes cuatro operaciones no se ejecutaron.

## Corrección
Se reemplazó `--format='value()'` por `--format=json >/dev/null` en los cinco comandos de escritura IAM. Se conservan los controles de proyecto, servicio privado, identidad de ejecución, limitación por recurso y confirmación explícita. Los comandos `add-iam-policy-binding` son seguros de repetir cuando la misma vinculación ya existe; la siguiente ejecución comprobará también la vinculación previa.

## Recuperación
En Cloud Shell:
```bash
cd ~/SmartRoute_AI
git pull --ff-only
bash scripts/gcp-bind-staging-deploy-iam.sh
CONFIRM_SMARTROUTE_DEPLOY_GRANTS=proyectopersonal-480420/smartroute-api-staging \
  bash scripts/gcp-bind-staging-deploy-iam.sh
```

La primera ejecución es simulación sin cambios y la segunda termina de aplicar los cinco permisos de alcance reducido. **No habilitar GitHub staging todavía**.

Si surge un nuevo fallo, detener y verificar cada vinculación antes de repetir. No conceder permisos a nivel de proyecto ni modificar recursos de otras aplicaciones.
