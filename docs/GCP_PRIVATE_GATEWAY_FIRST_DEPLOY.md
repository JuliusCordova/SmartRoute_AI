# Despliegue inicial PRIVADO del gateway SmartRoute

## Estado verificado por Cloud Shell
- `smartroute-gateway@proyectopersonal-480420.iam.gserviceaccount.com`: creada.
- `roles/run.invoker` concedido a esa identidad **solo** en `smartroute-api-staging`.
- Backend privado, ningún principal `allUsers` / `allAuthenticatedUsers` en su IAM directo.
- `GCP_STAGING_ENABLED=false`.
- Google Sign-In habilitado; proyecto Firebase Auth compartido con otras aplicaciones, no cambiar proveedores ni dominios.

## Script propuesto
`scripts/gcp-bootstrap-private-gateway.sh` valida la cuenta dedicada, el permiso backend-only, el repositorio Docker SmartRoute, el árbol Git limpio y la ausencia de un gateway preexistente. **Dry run** por defecto. Si se confirma, construye la imagen `smartroute-gateway` y la publica en `smartroute-staging`, obtiene digest inmutable, crea Cloud Run `smartroute-gateway-staging` en `us-central1`, usa cuenta de servicio dedicada y aplica:
- `--no-allow-unauthenticated`: gateway **privado** (no disponible aún para Android/web).
- Escalado 0 a 1 instancia, CPU 1, RAM 512Mi, concurrency 10, timeout 30s.
- `SMARTROUTE_GATEWAY_ENABLED=true`, `SMARTROUTE_BACKEND_URL` anclado al backend privado, `GOOGLE_CLOUD_PROJECT` aprobado.
- Verifica IAM del gateway sin acceso público.

No concede roles, no toca Firestore ni Firebase users, no altera otros servicios y no activa despliegue automático. La compilación/Artifact Registry/Cloud Run puede generar costos; **máximo de instancias no es límite de presupuesto**.

### Paso 1: solo simulación
```bash
cd ~/SmartRoute_AI
git pull --ff-only
bash scripts/gcp-bootstrap-private-gateway.sh
```

### Paso 2: ejecución real explícita por el propietario
```bash
CONFIRM_SMARTROUTE_GATEWAY_DEPLOY=proyectopersonal-480420/smartroute-gateway-staging \
  bash scripts/gcp-bootstrap-private-gateway.sh
```

### Validación siguiente
1. Obtener URL de Cloud Run y llamar `/health` usando una identidad con `run.invoker` del gateway, sin hacer público el endpoint.
2. Comprobar HTTP 401/403 para solicitudes sin Firebase ID token **una vez superada la autenticación Cloud Run IAM**.
3. Verificar token válido Firebase del usuario OPERATOR y permisos backend, sin cambiar política de otras aplicaciones.
4. Diseñar el control de exposición pública del gateway: antiabuso, CORS dominio web preciso, cuota/costos y autorización de cambios IAM. **No abrir públicamente automáticamente**.

La operación de health solo comprueba proceso, no autenticación Firebase ni persistencia. No implementar Cloud Run IAM token en Android: el gateway público necesitará su propia verificación Firebase tras aprobación y controles de seguridad.
