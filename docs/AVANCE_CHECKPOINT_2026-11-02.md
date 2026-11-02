# CHECKPOINT · SmartRoute AI · 2026-11-02

**Estado del Capstone al cierre de la sesión.** Documento para reanudar la ejecución en la siguiente sesión sin reconstruir contexto ni tocar recursos de otros proyectos.

## 1. Identificadores aprobados e invariantes

| Recurso | Valor |
|---|---|
| Repositorio | https://github.com/JuliusCordova/SmartRoute_AI |
| Proyecto GCP | `proyectopersonal-480420` |
| Número GCP | `913797829604` |
| Región | `us-central1` |
| Firestore exclusivo | Base nombrada `smartroute` |
| Bases NO tocar | `(default)`, `gestioncitas` |
| Artifact Registry exclusivo | `us-central1-docker.pkg.dev/proyectopersonal-480420/smartroute-staging` |
| API privada operativa | `smartroute-api-staging` |
| URL backend | `https://smartroute-api-staging-913797829604.us-central1.run.app` |
| Runtime backend | `smartroute-runtime@proyectopersonal-480420.iam.gserviceaccount.com` |
| Gateway SA creada | `smartroute-gateway@proyectopersonal-480420.iam.gserviceaccount.com` |
| Gateway Cloud Run pendiente | `smartroute-gateway-staging` |
| Otras cuentas | `smartroute-deployer`, `smartroute-smoke` |
| GitHub variables | Ocho configuradas; **`GCP_STAGING_ENABLED=false`** |
| Rama | `main` protegida: checks `api-tests` y `firestore-emulator`; no force push / delete |
| Entorno GitHub `staging` | Restringido a ramas protegidas |
| WIF | Pool `smartroute-ci`, provider `smartroute-main`, repositorio y rama `main` |

**Regla prioritaria:** GCP compartido con otros proyectos, incluido Firebase Authentication. No añadir project-wide roles, ni tocar otros Cloud Run, bases Firestore, usuarios existentes o proveedores/dominios Firebase. No abrir el backend privado; no publicar gateway sin un gate explícito de seguridad y costos.

## 2. Hitos comprobados

1. WIF manual GitHub→GCP, workflow preflight PASS (PR #31).
2. Primer CI/CD completo manual GitHub→Docker→Artifact Registry→Cloud Run privado PASS. Workflow `41396591290`, commit `3004c18`, health y ready autenticados PASS. Evidencia en `docs/GCP_FIRST_CICD_SUCCESS.md`.
3. Firestore real: orden sintética creada/leída, ruta asignada transaccionalmente y estado persistido PASS. Tres documentos sintéticos eliminados PASS, usando token efímero de la **cuenta runtime real**. Evidencia `docs/GCP_FIRESTORE_REAL_E2E_PASS.md`.
4. El permiso temporal `roles/iam.serviceAccountTokenCreator` del usuario `Julio.Cordova@gmail.com` sobre la SA runtime fue **retirado con éxito**. No repetir grant salvo necesidad expresa.
5. Firebase Identity Toolkit habilitado; API admin retornó HTTP 200 al añadir `x-goog-user-project: proyectopersonal-480420`. Email sign-in habilitado y **Google Sign-In `enabled:true`**. Hay dominios de otras apps; no modificarlos.
6. Gateway Firebase→Cloud Run IAM implementado, probado en CI e integrado (PR #38). Se usa cabecera `X-Serverless-Authorization` para Google IAM y `Authorization` para el token Firebase que FastAPI valida y cuyo rol comprueba en `users/{uid}` de la base `smartroute`. Código: `services/gateway/`.
7. Cuenta `smartroute-gateway` creada y **`roles/run.invoker` solo sobre `smartroute-api-staging`**, IAM de backend sin principals públicos a nivel de servicio. Evidencia reportada en Cloud Shell por propietario tras PR #39.
8. PR #40 añade bootstrap de Cloud Run gateway **privado**: `scripts/gcp-bootstrap-private-gateway.sh`. El propietario lo ejecutó, validó IAM y construyó correctamente Docker para commit `78c1104a5eb901f1225e3651be71f3c944593f88`.

## 3. Punto de interrupción EXACTO

**La compilación Docker del gateway pasó; el push a Artifact Registry falló por conectividad de Cloud Shell:**

```text
failed to do request: Head "https://us-central1-docker.pkg.dev/v2/...":
dial tcp 142.250.98.82:443: connect: connection refused
```

La imagen construida y etiquetada localmente fue:

```text
us-central1-docker.pkg.dev/proyectopersonal-480420/smartroute-staging/smartroute-gateway:78c1104a5eb901f1225e3651be71f3c944593f88
```

**No hay evidencia de que la imagen haya sido publicada ni que Cloud Run `smartroute-gateway-staging` haya sido creado.** No asumir que existe; verificar antes de operar. Backend privado no fue modificado.

## 4. Preparación para reanudar mañana

Para evitar recompilar Docker y dar roles adicionales se creó **PR #41**, probado en CI (`api-tests` y `firestore-emulator` PASS) y fusionado a `main` en commit `61cb79fa48956f2eb6381bfb4eb51f03ff6baaac`. Su script `scripts/gcp-recover-gateway-push.sh`:

- Exige imagen local exacta del commit `78c1104`; **no** reconstruye ni retaggea otra imagen.
- Revalida proyecto, identidad gateway, política privada del backend, repositorio Docker y ausencia de gateway preexistente.
- Hace hasta 4 intentos de `docker push`, extrae digest `sha256` validado y SOLO ENTONCES crea Cloud Run privado con el digest.
- Máximo 1 instancia, mínimo 0, RAM 512Mi, CPU 1, timeout 30s, cuenta exclusiva `smartroute-gateway`.
- No añade roles ni modifica Firestore o Firebase; no habilita `GCP_STAGING_ENABLED`.
- Posibles costos de publicación y Cloud Run. No hay presupuesto hard cap creado.

### Paso A — inspección/simulación SIN cambios

En Cloud Shell:

```bash
cd ~/SmartRoute_AI
git pull --ff-only
git status --short
bash scripts/gcp-recover-gateway-push.sh
```

Esperado: política IAM backend PASS, imagen local detectada, `DRY RUN: no Docker push or Cloud Run deployment.`

Si `git status` muestra solo `services/api/app/__pycache__/`, evaluar borrado **exclusivo** de ese directorio temporal; no usar `git clean -fd` ni `git reset --hard`. Para este recovery el script NO exige árbol Git limpio.

### Paso B — recuperación real, después de aprobar simulación

```bash
CONFIRM_SMARTROUTE_GATEWAY_RECOVERY=proyectopersonal-480420/smartroute-gateway-staging \
  bash scripts/gcp-recover-gateway-push.sh
```

**Importante:** si imagen Docker original no está en Cloud Shell (por reinicio), script detiene con error. En ese caso preparar rebuild explícito, anclado a revisión segura; no improvisar retag/uso de otra imagen. Si hay nueva falla de red, no modificar IAM ni hacer público Cloud Run.

### Paso C — comprobaciones posteriores (SIN abrir gateway)

Verificar mediante Cloud Shell:
- `gcloud run services describe smartroute-gateway-staging --project=proyectopersonal-480420 --region=us-central1`
- IAM del gateway sin `allUsers` / `allAuthenticatedUsers`, runtime SA correcta.
- HTTP `/health` **autenticado** con principal expresamente autorizado: solicitar permiso mínimo sobre el gateway si falta. Respuesta del proceso NO valida backend ni Firebase.
- Flujo de rechazo de token Firebase faltante e inválido, manteniendo IAM privado. Una llamada pública directa debe denegarse.
- Comprobar `gh variable get GCP_STAGING_ENABLED --repo JuliusCordova/SmartRoute_AI` = `false`.

## 5. Próximos hitos funcionales

1. Usuario de prueba con Google Sign-In: preparar cuenta de prueba y `users/{uid}` con `role=OPERATOR`, `active=true` **solo en base `smartroute`**; no modificar usuarios Firebase compartidos sin autorización. Planificar limpieza.
2. Probar HTTP E2E Firebase (token del usuario) → gateway → backend privado → órdenes/rutas → Firestore `smartroute`, negativos 401/403, creación y limpieza de documentos sintéticos.
3. Revisar cuotas/antiabuso/costo, dominios de origen web precisos y política de exposición antes de **considerar** un gateway público apto para Android/web.
4. Presupuesto/alertas, logging sin tokens, rollback de revisiones, comprobación de seguridad del pipeline; activar CI/CD continuo **solo** por decisión explícita.
5. Volver a plan académico: piloto Android + Google Maps + OR-Tools/Gemini consultivo, rutas comparables y métricas; actualmente las pruebas concluidas son de infraestructura y persistencia, no todavía de recorrido funcional Android.

## 6. Referencias de repositorio

- `docs/SECURE_MOBILE_WEB_GATEWAY.md`
- `docs/GCP_GATEWAY_IDENTITY_BOOTSTRAP.md`
- `docs/GCP_PRIVATE_GATEWAY_FIRST_DEPLOY.md`
- `docs/GCP_GATEWAY_PUSH_RECOVERY.md`
- `docs/GCP_FIRESTORE_REAL_E2E_PASS.md`
- `scripts/gcp-recover-gateway-push.sh`
- `services/gateway/app/main.py`

**Punto exacto de continuación:** verificar existencia de imagen Docker local y ejecutar el script de recuperación en simulación; no volver a configurar IAM/Firebase ni repetir pasos ya aprobados.
