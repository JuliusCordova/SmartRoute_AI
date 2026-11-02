# SmartRoute AI — Firestore creada; próximo gate IAM/WIF

## Evidencia de aprovisionamiento del usuario
**Confirmada mediante salida de Cloud Shell enviada por el usuario** (evento con `createTime=2026-11-02T04:28:34.908590Z`):
- Proyecto: `proyectopersonal-480420`, número `913797829604`
- Base de datos: `projects/proyectopersonal-480420/databases/smartroute`
- `databaseEdition: STANDARD`, `type: FIRESTORE_NATIVE`, `locationId: nam5`
- `deleteProtectionState: DELETE_PROTECTION_ENABLED`
- `freeTier: false`; `pointInTimeRecoveryEnablement: POINT_IN_TIME_RECOVERY_DISABLED`
- Resultado: operación de creación completada (`done: true`).

**No atribuir al asistente ejecución directa en GCP.** Fue ejecutado por el propietario en Cloud Shell. Las bases `(default)` (Atlas DataGob) y `gestioncitas` deben mantenerse intactas.

## Etapa siguiente: lectura segura del estado IAM
Ejecutar `bash scripts/gcp-iam-preflight.sh` desde Cloud Shell (tras merge y git pull). El script imprime únicamente metadatos mínimos; evita volcar la política IAM completa y no crea, habilita, cambia ni elimina nada.

## Diseño propuesto, NO aprovisionado todavía
1. Separar identidades `smartroute-runtime` (sólo Firestore dedicada), `smartroute-deployer` (publicación staging) y `smartroute-smoke` (sólo invocar servicio privado staging).
2. **Runtime Firestore**: dar `roles/datastore.user` bajo **condición IAM por nombre de recurso exacto** `resource.name == "projects/proyectopersonal-480420/databases/smartroute"`. Revisar interacción con otras políticas IAM existentes. No otorgar datastore.user sin condición a todo el proyecto compartido. Firestore soporta condiciones por base para SDK servidor; la consola web puede tener distinto comportamiento de IAM condicionado.
3. **GitHub WIF**: preferir pool/proveedor exclusivos y restringir a `JuliusCordova/SmartRoute_AI` y `refs/heads/main` con `assertion.repository_id` cuando esté disponible. Mapear atributo de repositorio y ref para IAM; no reutilizar ciegamente los cinco pools existentes del proyecto.
4. **Deployer Cloud Run desde código fuente**: validar requerimientos de `roles/run.sourceDeveloper`, `roles/serviceusage.serviceUsageConsumer`, build identity y `roles/iam.serviceAccountUser` limitado a runtime, según Google Cloud. Esos roles suelen requerir alcance de proyecto para crear servicios nuevos; revisar el riesgo en proyecto compartido, y preferir despliegue desde imagen y repositorio dedicado si un alcance menor es necesario.
5. **Smoke IAM**: cuenta separada con invocación `roles/run.invoker` restringida al nuevo servicio `smartroute-api-staging`. La API actual usa Firebase ID token para rutas de negocio; esto es distinto del token de invocación IAM de Cloud Run: no afirmar E2E Android/API sin resolver ese doble control.
6. **Costos**: alertas y monitoreo no son límites estrictos de gasto. Revisar presupuesto compartido, cuota Cloud Run, Cloud Build y Firestore; no habilitar staging hasta tener revisión IAM/costos.

## Estado operativo
`GCP_STAGING_ENABLED` debe permanecer `false`/ausente. No se han creado cuentas de servicio para SmartRoute, identidad WIF, servicio Cloud Run ni verificado persistencia de producción desde este procedimiento.

## Referencias oficiales
- https://firebase.google.com/docs/firestore/manage-databases
- https://firebase.google.com/docs/firestore/security/iam
- https://docs.cloud.google.com/run/docs/reference/iam/roles
- https://github.com/google-github-actions/auth
