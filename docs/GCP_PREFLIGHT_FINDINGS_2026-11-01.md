# Evidencia del preflight GCP — SmartRoute AI

**Fecha reportada:** 2026-11-01 (Cloud Shell, proporcionado por el usuario). **Estado:** INVENTARIADO; ninguna acción de aprovisionamiento ejecutada por este trabajo.

## Resultado observado — proyecto compartido
- Proyecto: `proyectopersonal-480420` / número `913797829604`, estado ACTIVE.
- Firestore Native: bases **`(default)`** y **`gestioncitas`**, ambas ubicadas en `nam5`. El comando de inventario no reportó edición; confirmar con `gcloud firestore databases describe`. **No conocemos colecciones, propietarios ni base gratuita elegible.**
- Cloud Run: existen múltiples servicios activos, incluidos `atlas-datagob-*`, `business-rules-*`, `ayniq-prod`, `prima-demo-*`, `silver-refinement-*`, `jarvis-*`. **No aparece servicio `smartroute-*`** en la salida.
- Identidades SmartRoute: ninguna listada por el filtro del preflight.
- Workload Identity Pools: `ayn-iac-github`, `ayniq-iac-github`, `ayn-iac-agent-github`, `primademo-github`, `github-actions`. No dar por hecho que `github-actions` sea seguro o esté preparado para SmartRoute.
- APIs habilitadas observadas: Artifact Registry, Cloud Build, Firestore, IAM Credentials, Cloud Run, STS.

## Decisión y riesgos
El proyecto seleccionado es compartido; **NO crear una nueva base ni escribir en `(default)` sin confirmar previamente las colecciones/propiedad**. La base `gestioncitas` no se reutiliza para SmartRoute. La cuota gratuita de Firestore solo cubre una base por proyecto y **no** se suma por cada base nombrada. Con dos bases existentes, una base adicional probablemente implique facturación por operaciones. Consultar: https://firebase.google.com/docs/firestore/pricing

El SDK actual del backend utiliza `(default)` por omisión y colecciones genéricas `orders`, `routes`, `users`, `drivers`: existe riesgo material de colisión incluso si las APIs y IAM ya están habilitadas.

## Segundo preflight: inspección segura de la base, sin documentos ni datos personales
Ejecutar en Cloud Shell:

```bash
gcloud firestore databases describe --project=proyectopersonal-480420 --database='(default)' --format='yaml(name,locationId,type,edition,deleteProtectionState)'
gcloud firestore databases describe --project=proyectopersonal-480420 --database=gestioncitas --format='yaml(name,locationId,type,edition,deleteProtectionState)'
```

Para **ver nombres de colecciones**, usar consola [Firestore](https://console.cloud.google.com/firestore/databases?project=proyectopersonal-480420), seleccionar `(default)` → Data y reportar **solo nombres** de las colecciones de primer nivel, sin exportar documentos ni PII. Esto evita publicar contenidos de otras aplicaciones.

Si hay dudas sobre la función actual de `(default)`, detener el despliegue de SmartRoute y evaluar (a) proyecto nuevo para aislamiento y free tier propio, (b) base con nombre explícito + adaptación SDK y presupuesto, o (c) namespace de colecciones bajo aislamiento de roles revisado. **No** presuponer que un prefijo permite IAM por colección en el SDK servidor.

## Próximo gate
1. Confirmar colección/propiedad de `(default)`, edición, quién consume la cuota gratuita y si la base está destinada a otras aplicaciones.
2. Elegir aislamiento, región y presupuesto. No reutilizar pools WIF actuales sin auditar su condición de repositorio/ref y permisos.
3. Crear WIF e identidades mínimas para SmartRoute únicamente tras aprobar el aislamiento.
4. Activar GitHub staging cuando existan permisos y checks requeridos. Hasta entonces `GCP_STAGING_ENABLED=false`.

**No se ha desplegado Cloud Run, creado cuentas ni configurado Firestore.**
