# SmartRoute gateway: recuperación después de reinicio de Cloud Shell

El propietario ejecutó el dry-run de `scripts/gcp-recover-gateway-push.sh` y obtuvo que la imagen original de commit `78c1104a5eb901f1225e3651be71f3c944593f88` **no está en Docker local**. La identidad y políticas del backend sí pasaron; no se ejecutó publicación ni despliegue.

## Recuperación aprobable

El nuevo `scripts/gcp-rebuild-gateway-private.sh` reconstruye la imagen solo cuando:
- Se ejecuta en `main`, árbol limpio y commit igual al `origin/main` local.
- El contenido de `services/gateway/` es idéntico al contenido revisado en `78c1104a5eb901f1225e3651be71f3c944593f88`; si no, aborta.
- Existen el Artifact Registry Docker dedicado, la cuenta runtime exclusiva y el backend privado con `roles/run.invoker` solo para esa cuenta, sin principales públicos de servicio.
- Todavía **no** existe Cloud Run `smartroute-gateway-staging`.

Hace dry run sin crear recursos. La ejecución explícita hace una compilación, reintenta hasta cuatro veces el push de la imagen en el registro SmartRoute, exige digest SHA256 y crea **solo** el Cloud Run gateway privado (min 0, max 1, 512Mi, CPU 1) con la cuenta dedicada. No modifica IAM, Firebase, otras apps ni `GCP_STAGING_ENABLED=false`. Docker build/Artifact Registry/Cloud Run podrían generar costos.

### 1. Simulación
```bash
cd ~/SmartRoute_AI
git pull --ff-only
git status --short
bash scripts/gcp-rebuild-gateway-private.sh
```
Debe terminar `DRY RUN: no Docker build, push or Cloud Run deployment.`

### 2. Despliegue inicial, si la simulación pasa
```bash
CONFIRM_SMARTROUTE_GATEWAY_REBUILD=proyectopersonal-480420/smartroute-gateway-staging \
  bash scripts/gcp-rebuild-gateway-private.sh
```

Si el gateway ya fue creado, el script aborta sin sobrescribirlo; inspeccionarlo antes. Si hay error de red tras los intentos, registrar error y detenerse, sin modificar IAM. Luego probar el gateway con invocación IAM autenticada y rechazos Firebase; **no hacerlo público** todavía.
