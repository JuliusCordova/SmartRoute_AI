# Staging backend desplegado — evidencia Cloud Shell

**Confirmado por el usuario**, en salida de despliegue de recuperación del 2026-11-02 (UTC):
- Artifact Registry: `us-central1` / `smartroute-staging`; imagen `smartroute-api`.
- Docker push exitoso tras dos fallos de red (`connect: connection refused`) y en el tercer intento.
- Commit de la imagen: `da8df041d240f0868488741116f913d57e0a0d6d`.
- Digest: `sha256:ae202c8d092a02ae416cc0a2c5b246259b98946a0b2204d10376795c05591a10`.
- Cloud Run: `smartroute-api-staging`, revisión `smartroute-api-staging-00001-2vt`, 100 % del tráfico.
- URL: `https://smartroute-api-staging-913797829604.us-central1.run.app`.
- Runtime: `smartroute-runtime@proyectopersonal-480420.iam.gserviceaccount.com`.
- `Ready=True`, `ConfigurationsReady=True`, `RoutesReady=True`.
- GitHub Actions staging **aún desactivado**: `GCP_STAGING_ENABLED` ausente/false.

## Lo que NO prueba esta evidencia
No se ha probado `/health` ni `/ready` vía token IAM, acceso real a la base Firestore `smartroute`, la autenticación Firebase ni el flujo Android/Web. No se han concedido a GitHub permisos de Artifact Registry/Cloud Run, ni los de invocación de smoke.

## Verificación operativa recomendada
Ejecutar en Cloud Shell el script `scripts/gcp-verify-staging-http.sh`, que crea un proxy local autenticado a la API privada, llama `/health` y `/ready` y cierra el proxy. **No** activa GitHub Actions ni modifica servicio/FireStore/IAM.

## Siguiente gate
Crear vínculos mínimos sobre los recursos ya existentes: `artifactregistry.writer` en el repositorio exclusivo, `run.developer` sólo en el servicio, `iam.serviceAccountUser` sobre runtime, e invocación `run.invoker` sobre ese servicio para smoke. Revalidar el procedimiento OIDC de emisión de token para la identidad smoke. No habilitar `GCP_STAGING_ENABLED` antes de completar este gate.
