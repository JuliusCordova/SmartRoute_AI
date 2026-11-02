# SmartRoute — prueba E2E real de Firestore (base nombrada)

## Objetivo
Confirmar usando credenciales **temporales de la identidad real `smartroute-runtime`** que el backend puede ejecutar operaciones de datos contra `projects/proyectopersonal-480420/databases/smartroute`, sin usar `(default)` ni `gestioncitas`.

## Datos y procedimiento
Script propietario `scripts/gcp-firestore-runtime-e2e.sh` (dry run por defecto) y prueba `scripts/gcp-firestore-runtime-e2e.py`. Utiliza el modelo de órdenes y rutas y los repositorios `FirestoreOrderRepository` y `FirestoreRouteRepository` del backend:

1. Verifica proyecto, base y ausencia del emulador; Cloud Shell con `gcloud` autenticado.
2. Solicita a `gcloud auth print-access-token --impersonate-service-account=smartroute-runtime@...` una credencial efímera, sin claves JSON. **La cuenta que opera Cloud Shell debe disponer de `iam.serviceAccounts.getAccessToken` en esta cuenta**, de lo contrario aborta y no modifica IAM.
3. Crea un conductor sintético, una orden y una ruta con IDs UUID únicos.
4. Comprueba lectura de orden, transacción de asignación, estado `ASSIGNED`, versionado y vinculación de ruta.
5. En un bloque `finally`, elimina exclusivamente las **tres referencias creadas para esta ejecución** (no hace limpieza global ni escanea otras colecciones). Si alguna eliminación falla, imprime solo los IDs afectados para una limpieza manual puntual.

## Ejecución en Cloud Shell
**Paso 1 — Simulación (sin escrituras)**

```bash
cd ~/SmartRoute_AI
git pull --ff-only
bash scripts/gcp-firestore-runtime-e2e.sh
```

**Paso 2 — Prueba real autorizada con datos sintéticos y limpieza**

```bash
CONFIRM_SMARTROUTE_FIRESTORE_TEST=proyectopersonal-480420/smartroute \
  bash scripts/gcp-firestore-runtime-e2e.sh
```

El script crea un entorno Python aislado de corta vida en `/tmp`, instala dependencias Firestore/Pydantic y elimina ese entorno al terminar. Si falla la autenticación del runtime, **no conceder Token Creator sobre el proyecto completo**; revisar si corresponde conceder temporalmente un permiso en esa cuenta exclusivamente, con autorización específica.

## Criterios de aceptación
`PASS: create/read synthetic order as runtime`
`PASS: atomic synthetic route assignment and persisted read`
`PASS: removed only 3 uniquely identified synthetic test documents`
`PASS: real Firestore named-database E2E with impersonated runtime`

Esta prueba valida permisos efectivos y repositorios de datos, pero no el endpoint HTTP con Firebase Auth, que requiere otro escenario con usuario de prueba registrado y un mecanismo de entrada compatible con Cloud Run privado.

## Referencias
- https://docs.cloud.google.com/docs/authentication/use-service-account-impersonation
- https://docs.cloud.google.com/python/docs/reference/firestore/latest/google.cloud.firestore_v1.client
