# SmartRoute AI — staging en GCP compartido (proyectopersonal-480420)

**Preflight ejecutado (2026-11-01):** ya existen dos bases Firestore en `nam5`, `(default)` y `gestioncitas`, y varios servicios Cloud Run. **La captura posterior confirma que `(default)` contiene colecciones de Atlas DataGob: queda PROHIBIDO usarla para SmartRoute.** Revisar [hallazgos del preflight](GCP_PREFLIGHT_FINDINGS_2026-11-01.md).

**Decisión de usuario:** reutilizar `proyectopersonal-480420` para SmartRoute AI. **Estado:** proyecto seleccionado y automatización definida en GitHub, **sin acceso de este asistente a GCP, ni recursos inspeccionados, creados o desplegados**. Repositorio `JuliusCordova/SmartRoute_AI`.

## 0. Inventario obligatorio y control de costos
En **Cloud Shell**, ejecutar desde un clon del repositorio:
```bash
git clone https://github.com/JuliusCordova/SmartRoute_AI.git
cd SmartRoute_AI
bash scripts/gcp-preflight.sh
```
El script es **solo lectura**. Revisar las bases Firestore existentes y Cloud Run antes de aplicar nada.

**Decisión de persistencia:** el SDK se actualizó para exigir `FIRESTORE_DATABASE_ID` y rechazar las bases ajenas al proyecto SmartRoute; **no** usa `(default)` por defecto fuera del emulador. Antes de crearla, verificar si existe y si ya contiene datos de otros proyectos. No reutilizar una base existente con otras apps: las colecciones `orders`, `users` y `routes` podrían colisionar. La cuota gratis de Firestore solo cubre una base por proyecto; las bases adicionales o con ID distinto pueden facturarse y necesitar adaptación del SDK. Si la base `(default)` está ocupada, **DETENER** la activación: decidir explícitamente entre aislamiento en proyecto propio, base nombrada con costo e implementación `database=...`, o un nuevo diseño con prefijos de colecciones. No borrar ni migrar información existente por comodidad.

**Presupuesto:** asignar alerta específica a SmartRoute si el sistema de facturación permite distinguir consumo por servicios/etiquetas; los presupuestos NO son un límite de gasto. Establecer cuotas y revisar facturación de Routes API, Gemini, Cloud Run, Cloud Build y Firestore. Nunca exponer la API públicamente para probarla.

## 1. Parámetros previstos
| Variable | Valor |
|---|---|
| `GCP_PROJECT_ID` | `proyectopersonal-480420` (fijo en workflow como guardrail) |
| `GCP_REGION` | decidir según disponibilidad/costo; por definir |
| `GCP_STAGING_ENABLED` | dejar ausente/false hasta completar pruebas del runbook |
| `GCP_FIRESTORE_DATABASE_ID` | `smartroute` (nombre propuesto; base aún no creada, costo por uso pendiente de aprobación) |
| `GCP_WIF_PROVIDER` | creado tras aprobar permisos IAM |
| `GCP_DEPLOYER_SERVICE_ACCOUNT` | `smartroute-deployer@proyectopersonal-480420.iam.gserviceaccount.com` (propuesta) |
| `GCP_RUNTIME_SERVICE_ACCOUNT` | `smartroute-runtime@proyectopersonal-480420.iam.gserviceaccount.com` (propuesta) |
| `GCP_SMOKE_SERVICE_ACCOUNT` | `smartroute-smoke@proyectopersonal-480420.iam.gserviceaccount.com` (propuesta) |

Las direcciones son **nombres propuestos**, no cuentas creadas. Toda creación y habilitación de APIs queda fuera del script de inventario.

## 2. Aprovisionamiento controlado (solo después de inventario y decisión de costos)
1. **La base `(default)` ya está ocupada por Atlas DataGob y no debe utilizarse.** El camino propuesto es una base nombrada **`smartroute`**, sujeta a aprobación de facturación y cuota. Configurar la ubicación compatible con la aplicación, preferentemente revisando `nam5` y región Cloud Run; verificar edición Standard y protección contra eliminación antes de crearla. No ejecutar comandos de creación hasta que el dueño autorice el costo.
2. Vincular Firebase Authentication al proyecto existente sin cambiar otros proveedores/configuraciones usados por aplicaciones preexistentes; activar únicamente métodos necesarios para usuarios de prueba. Crear usuarios ficticios y perfiles `users/{uid}` administrativamente, con `role: OPERATOR` y `active: true`, sin tokens ni claves en Git.
3. Habilitar solo APIs necesarias para Cloud Run/Cloud Build/Artifact Registry/IAM Credentials/STS/Firestore; ninguna de estas operaciones se ejecuta desde CI antes de esta autorización.
4. Crear tres identidades distintas de servicio (deployer, runtime, smoke) y políticas mínimas; revisar el alcance de roles sobre este proyecto compartido.
5. Crear un Workload Identity Pool `smartroute-ci` y un OIDC provider GitHub `smartroute-main` con condición **simultánea** `assertion.repository == 'JuliusCordova/SmartRoute_AI'` y `assertion.ref == 'refs/heads/main'`. Incluir `google.subject=assertion.sub` y `attribute.repository=assertion.repository`; usar `principalSet://iam.googleapis.com/projects/<NUMBER>/locations/global/workloadIdentityPools/smartroute-ci/attribute.repository/JuliusCordova/SmartRoute_AI` en las vinculaciones de cada cuenta. Si la organización/política permite, restringir aún más por `repository_id` inmutable y entorno.
6. Conceder al deployer solo permisos necesarios para Cloud Run + build/artifacts y `roles/iam.serviceAccountUser` **exclusivamente sobre** la cuenta runtime. Dar a runtime el mínimo acceso de datos al Firestore existente (IAM es a menudo a nivel proyecto; revisar). La cuenta smoke necesita `roles/run.invoker` **sobre el servicio staging**, no sobre todo el proyecto, y permisos apropiados para emitir su token OIDC de corta duración.
7. Crear un **Environment staging** en GitHub permitiendo despliegue solo desde `main`; configurar protección de rama y checks `api-tests` + `firestore-emulator` obligatorios.
8. Configurar las seis variables descritas arriba en GitHub Repository Actions; `GCP_STAGING_ENABLED=false` hasta que todas estén verificadas. Activar `true` solamente después de autorización de costos y mínimo privilegio.

### Comandos de ejemplo (NO ejecutados; administración manual)

```bash
PROJECT_ID=proyectopersonal-480420
# Verificar primero inventario, facturación, región, base Firestore y permisos.
gcloud config set project "$PROJECT_ID"

# Ejemplo SOLO si no existe (default) y un administrador ya aprobó su ubicación/costo:
# gcloud firestore databases create --project="$PROJECT_ID" \
#   --database="(default)" --edition=standard --type=firestore-native \
#   --location="REGION_ELEGIDA" --delete-protection

# Ejemplo de creación de un proveedor OIDC únicamente tras aprobación:
# gcloud iam workload-identity-pools providers create-oidc smartroute-main \
#   --project="$PROJECT_ID" --location=global \
#   --workload-identity-pool=smartroute-ci \
#   --issuer-uri="https://token.actions.githubusercontent.com" \
#   --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
#   --attribute-condition="assertion.repository=='JuliusCordova/SmartRoute_AI' && assertion.ref=='refs/heads/main'"
```

No usar llaves JSON de cuentas de servicio en GitHub. GitHub Actions sólo consume la identidad federada, no crea el pool, cuentas, permisos o presupuesto.

## 3. Pipeline y validación
Workflow: `.github/workflows/ci.yml`. Primero `api-tests` + `firestore-emulator`; tras un merge autorizado en `main`, `deploy-staging` se ejecuta únicamente si `vars.GCP_STAGING_ENABLED == 'true'` y `vars.GCP_PROJECT_ID == 'proyectopersonal-480420'`.

El smoke emplea OIDC para la cuenta **smartroute-smoke** y prueba `/health` y `/ready`; este último valida solo el proceso. Un smoke adicional de Firebase ID token + Firestore real se diseñó como [Issue #12](https://github.com/JuliusCordova/SmartRoute_AI/issues/12). No afirmar integración real o despliegue hasta tener resultados verificables y URI de la revisión.

## 4. Evidencia exigida (antes de marcar DEPLOYED)
- Inventario con fecha y decisión sobre Firestore `(default)`, ocultando datos sensibles.
- Confirmación región y presupuesto/quota de uso.
- Captura/configuración WIF/IAM y GitHub Environment; sin secretos.
- Workflow completado en `main` con Cloud Run staging, URL, revisión/commit, smoke IAM satisfactorio y rollback de revisión.
- Prueba funcional autenticada de pedidos y rutas en Firestore real; costos observados.

## 5. Referencias
- https://cloud.google.com/firestore/pricing
- https://docs.cloud.google.com/firestore/native/docs/manage-databases
- https://github.com/google-github-actions/auth
- https://docs.cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines

**Stop conditions:** datos ajenos en la base default; prohibición de OAuth provider; permisos insuficientes; facturación/alertas no verificadas; cambio de API o de configuración compartida con impacto. Ante cualquiera, mantener `GCP_STAGING_ENABLED=false`.

## Autorización específica para crear la base (2026-11-01)
El titular aprobó explícitamente crear una base independiente **`smartroute`** en `proyectopersonal-480420` con protección contra eliminación. La base `(default)` se encuentra ocupada por Atlas DataGob y `gestioncitas` pertenece a otra aplicación. La creación no equivale a autorizar cambios IAM, habilitar producción ni desplegar Cloud Run.

El comando oficial de Google Cloud para Standard Native permite `--database`, `--location`, `--edition=standard`, `--type=firestore-native` y `--delete-protection`. Se eligió `nam5` para coincidir con la ubicación de las bases existentes; verificar latencia y requisitos legales antes de incorporar datos reales. **No hay cuota gratuita para esta base nombrada** y los presupuestos solo alertan, no bloquean automáticamente gastos.

Ejecutar desde Cloud Shell en una copia actualizada de `main`:
```bash
cd ~/SmartRoute_AI
git pull --ff-only
CONFIRM_CREATE_SMARTROUTE_DB=proyectopersonal-480420/smartroute \
  bash scripts/gcp-create-smartroute-db.sh
```

La operación de creación es idempotente frente a una base ya existente (en ese caso no modifica nada). El comando final `describe` debe indicar `name: projects/proyectopersonal-480420/databases/smartroute`, `locationId: nam5`, `type: FIRESTORE_NATIVE` y `deleteProtectionState: DELETE_PROTECTION_ENABLED`. La edición puede omitirse en algunas versiones de respuesta; se solicita explícitamente Standard en la creación. No usar claves de servicio descargadas ni modificar Firestore Rules de Atlas.

**Siguiente gate:** verificar IAM segregado, OIDC WIF y presupuesto/alertas; `GCP_STAGING_ENABLED` permanece desactivado.
