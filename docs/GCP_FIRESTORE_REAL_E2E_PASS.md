# Evidencia: prueba real de persistencia Firestore SmartRoute — PASS

Fecha reportada: 2026-11-02. Evidencia: salida de Cloud Shell facilitada por el propietario.

## Alcance ejecutado
- Proyecto `proyectopersonal-480420`, **base nombrada `smartroute`**.
- Identidad efectiva: token efímero impersonado de `smartroute-runtime@proyectopersonal-480420.iam.gserviceaccount.com`.
- Script `scripts/gcp-firestore-runtime-e2e.sh`; sin escrituras en otras bases; sin cambios en Cloud Run ni en GitHub Actions.

## Evidencia de resultados
```text
PASS: database and impersonated runtime identity pinned; token not logged
PASS: create/read synthetic order as runtime
PASS: atomic synthetic route assignment and persisted read
PASS: removed only 3 uniquely identified synthetic test documents
PASS: real Firestore named-database E2E with impersonated runtime
```

El script creó exactamente un conductor, una orden y una ruta sintéticos con IDs únicos, comprobó asignación transaccional y datos persistidos y eliminó las tres referencias creadas. No fue una prueba de endpoints HTTP autenticados con Firebase.

## Cierre de IAM temporal
El propietario ejecutó `remove-iam-policy-binding` sobre el **único** principal `user:Julio.Cordova@gmail.com` con `roles/iam.serviceAccountTokenCreator` en `smartroute-runtime`, y el resultado mostró la política de la cuenta sin esta vinculación:

```text
bindings:
- members:
  - serviceAccount:smartroute-deployer@proyectopersonal-480420.iam.gserviceaccount.com
  role: roles/iam.serviceAccountUser
```

La salida confirma revocación **de ese binding directo**. No se ha auditado acceso efectivo por herencia ni permisos de otros principales.

## Próximos gates
1. Firebase Auth: verificar ID token de usuario real de prueba y rol OPERATOR server-side en Firestore nombrado, sin generar claves permanentes.
2. Arquitectura de entrada Android/React: separar la autenticación de invocación Cloud Run IAM del bearer Firebase ID token del aplicativo; no publicar el backend ni usar service tokens en la app.
3. Prueba HTTP E2E con orden/ruta sintéticas y limpieza, incluyendo rechazo de llamadas sin identidad, verificando permisos y observabilidad.
4. Presupuesto/alertas y restauración/rollback de la revisión publicada.
5. **`GCP_STAGING_ENABLED=false`** hasta activar CI/CD continuo explícitamente.
