# SmartRoute: recuperación de publicación fallida del gateway

## Incidente
Cloud Shell terminó `docker build` de `smartroute-gateway` con éxito usando la revisión de código `78c1104a5eb901f1225e3651be71f3c944593f88`. Durante `docker push` a Artifact Registry `us-central1-docker.pkg.dev`, la conexión TCP 443 fue rechazada (`connect: connection refused`). **Cloud Run gateway no se creó en esa ejecución.** No hay indicios de fallo de aplicación o autorización IAM.

## Recuperación
`scripts/gcp-recover-gateway-push.sh` reutiliza expresamente la etiqueta local original asociada al commit anterior, sin reconstruir ni reemplazarla con el commit nuevo. Se detiene si la imagen local ya no está disponible, la identidad es incorrecta, cambió el backend o existe un gateway Cloud Run (evita sobrescrituras).

- Dry-run por defecto; el usuario debe habilitarlo explícitamente.
- Hasta cuatro intentos de publicación Docker, con espera breve entre intentos.
- Exige obtener digest SHA256 válido; solo entonces publica la imagen por **digest inmutable** en el nuevo Cloud Run `smartroute-gateway-staging`.
- Servicio privado (`--no-allow-unauthenticated`), una instancia como máximo, con cuenta dedicada del gateway y URL fija al backend privado.
- Verifica ausencia de principals públicos directos en IAM del servicio.
- Sin cambios de Firebase, Firestore ni IAM, sin activar CI/CD continuo.

## Ejecución por el propietario
```bash
cd ~/SmartRoute_AI
git pull --ff-only
bash scripts/gcp-recover-gateway-push.sh
```

Resultado esperado: `DRY RUN: no Docker push or Cloud Run deployment.`

Tras inspeccionar:
```bash
CONFIRM_SMARTROUTE_GATEWAY_RECOVERY=proyectopersonal-480420/smartroute-gateway-staging \
  bash scripts/gcp-recover-gateway-push.sh
```

Si el script informa que la imagen ya no está presente, no retaggear una imagen distinta ni conceder permisos amplios. Reportar el resultado para preparar rebuild controlado.

**Los reintentos de publicación y el servicio nuevo pueden generar costos; estos límites de escalado no son presupuestos máximos.**
