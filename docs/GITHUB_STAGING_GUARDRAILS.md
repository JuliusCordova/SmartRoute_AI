# GitHub branch and staging environment guardrails

## Diagnóstico reportado por el propietario
- `GET /environments/staging` devolvió 404: entorno aún no disponible/no accesible.
- `GET /branches/main/protection` devolvió 404: `main` no protegida.
- Repositorio `JuliusCordova/SmartRoute_AI` confirmado **público** por GitHub.
- Variables del repositorio creadas con `GCP_STAGING_ENABLED=false`.
- WIF manual privado `verify-wif-private-smoke` terminó satisfactoriamente.

## Configuración recomendada
El script `scripts/github-protect-staging.sh` evita aplicar el cambio por defecto: solo muestra plan hasta recibir confirmación explícita. Rechaza sobrescribir reglas existentes, comprueba visibilidad pública y exige `GCP_STAGING_ENABLED=false`.

Al aplicar:
1. Protege rama `main`, requiere `api-tests` y `firestore-emulator` con estado actualizado (strict), deshabilita force pushes y borrados y exige conversaciones resueltas. No exige otro revisor por ahora, no obliga al administrador a cumplir checks porque la automatización actual utiliza merges del propietario.
2. Crea entorno GitHub `staging`, con política de **ramas protegidas** y no otras ramas.
3. Verifica ambas configuraciones e invariante `GCP_STAGING_ENABLED=false`.

### Ejecutar desde Cloud Shell
```bash
cd ~/SmartRoute_AI
git pull --ff-only
bash scripts/github-protect-staging.sh
```
Revisar salida DRY RUN. Con confirmación:
```bash
CONFIRM_SMARTROUTE_GH_PROTECTION=JuliusCordova/SmartRoute_AI bash scripts/github-protect-staging.sh
```

**Advertencias:** la protección puede impedir merges directos o afectar un flujo de PR si checks no se publican correctamente; por eso comprobar inmediatamente los resultados. No confundir entorno restringido con revisión humana obligatoria: para repositorios públicos se podría habilitar después, pero requerir un segundo revisor podría entorpecer el trabajo individual. No activar staging hasta los ensayos de build/push por digest y presupuesto.

## Referencias oficiales
- https://docs.github.com/en/rest/branches/branch-protection
- https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments
