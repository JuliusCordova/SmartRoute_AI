# SmartRoute AI — primera publicación manual completa de staging

## Evidencia de ejecución (2 de noviembre de 2026)
- Workflow: `SmartRoute controlled manual staging deployment`.
- Run: https://github.com/JuliusCordova/SmartRoute_AI/actions/runs/41396591290
- Evento: `workflow_dispatch`, rama `main`, commit `3004c181bbd7898bbba16511dcddf4495c8ef724`.
- Conclusión: **success** (captura del propietario y comprobación de jobs desde GitHub).
- Duración reportada en interfaz: **1m 34s**.
- Job `manual-staging-deploy`: **success**.

### Pasos del workflow que GitHub confirmó exitosos
1. Validación de configuración anclada y bandera de despliegue continuo desactivada.
2. Autenticación WIF de `smartroute-deployer`.
3. Verificación del repositorio Artifact Registry y servicio Cloud Run dedicados.
4. Construcción y publicación Docker con digest inmutable.
5. Despliegue de imagen al servicio privado `smartroute-api-staging`.
6. Autenticación WIF de `smartroute-smoke` e invocación autenticada de `/health` y `/ready`.
7. Registro de evidencias del despliegue.

## Lo que está comprobado y lo que no
**Comprobado:** el circuito manual de GitHub Actions a Artifact Registry y Cloud Run privado funciona con identidades dedicadas; los endpoints de salud responden.

**No comprobado todavía:** lectura/escritura real en Firestore nombrado `smartroute`, flujos con token de usuario Firebase Auth, acceso Android/React a Cloud Run privado, pruebas funcionales de órdenes y optimización de rutas en infraestructura real, rollback y presupuesto/alertas.

**Estado de CI/CD continuo:** `GCP_STAGING_ENABLED=false`. Un workflow manual exitoso no habilita despliegue automático en cada push.

## Gates recomendados
- Ensayo de persistencia acotado a datos sintéticos del Firestore `smartroute` usando runtime identity y sin tocar `(default)` ni `gestioncitas`.
- Diseño del acceso móvil y web sin debilitar autenticación IAM/Firebase.
- Revisión de presupuesto y alertas (no son límites duros).
- Validación de rollback y registro de digest / revisión publicada.
- Activar CI/CD continuo sólo con decisión explícita del propietario.
