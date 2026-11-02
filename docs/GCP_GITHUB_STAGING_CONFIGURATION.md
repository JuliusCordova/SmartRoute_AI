# SmartRoute — WIF manual PASS y preparación controlada de CI/CD

## Evidencia validada
En la captura del usuario, **SmartRoute manual WIF staging preflight #1** ejecutado sobre rama `main` commit `1fa487c` completó con **Success**; job `verify-wif-private-smoke` en verde (duración de workflow 29s).

El workflow valida GitHub WIF para `smartroute-deployer` y `smartroute-smoke`, metadatos de repositorio y Cloud Run, y smoke privado `/health` + `/ready`. No despliega código. No se debe interpretar como validación de Firebase Auth o persistencia Firestore.

## Paso siguiente en Cloud Shell (GitHub CLI)
```bash
cd ~/SmartRoute_AI
git pull --ff-only
gh auth status
bash scripts/github-configure-staging-vars.sh
```
Simulación: no escribe variables.

Con la autorización del propietario para la configuración del repositorio:
```bash
CONFIRM_SMARTROUTE_GH_VARS=JuliusCordova/SmartRoute_AI \
  bash scripts/github-configure-staging-vars.sh
```
Configura los parámetros explícitos de proyecto, región, WIF, base Firestore `smartroute` y cuentas dedicadas. **Establece GCP_STAGING_ENABLED=false**, no activa ni ejecuta el despliegue. Las variables no son secretos y no incluyen claves privadas.

La acción requiere `gh` autenticado con permiso para modificar variables del repositorio. Si `gh` no existe, configurar manualmente en GitHub → Settings → Secrets and variables → Actions → Variables, manteniendo el flag false.

## Pendientes para el primer deploy automatizado
- Revisar el Environment `staging` y reglas de protección / rama `main`.
- Validar los permisos efectivos de Docker push y revisión Cloud Run con la identidad de CI (WIF preflight solo consultó metadatos).
- Comprobar que GitHub Actions puede publicar imagen con digest inmutable. El pipeline reemplazó el parser sed ambiguo por awk que extrae literalmente el campo posterior a `digest:`.
- Definir activación expresa del CI/CD solo tras comprobar reglas de protección, costo y seguridad del proyecto compartido.
- Asegurar que clientes Android/React accedan mediante patrón que preserve Cloud Run IAM y Firebase Auth sin exponer el servicio indiscriminadamente.
- Probar persistencia de Firestore en la base propia `smartroute` sin tocar `(default)` ni `gestioncitas`.

**No habilitar GCP_STAGING_ENABLED en este paso.**
