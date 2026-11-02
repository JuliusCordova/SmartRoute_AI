# SmartRoute gateway: bootstrap aislado de identidad

## Evidencia de inventario del propietario
`gcloud iam service-accounts list --filter='email:smartroute-gateway'`: sin resultados.
`gcloud run services list --filter='metadata.name=smartroute-gateway-staging'`: sin resultados.
`gh variable get GCP_STAGING_ENABLED`: `false`.

La autenticación Firebase Google Sign-In se verificó habilitada (`enabled: true`), Identity Toolkit y lectura de configuración `HTTP 200`. El proyecto es compartido con otras apps: **no modificar la configuración de Firebase existente**.

## Cambio acotado
`scripts/gcp-bootstrap-gateway-identity.sh` hace dry run por defecto. Al autorizar:
- Crea `smartroute-gateway@proyectopersonal-480420.iam.gserviceaccount.com`.
- Otorga **roles/run.invoker solo sobre `smartroute-api-staging`** a esa cuenta.
- Verifica la identidad de runtime del backend y que su política IAM no contiene `allUsers` ni `allAuthenticatedUsers`.
- Aborta si ya encuentra la cuenta del gateway o servicio gateway, evitando alterar recursos existentes.
- **No despliega servicio, no publica imágenes, no habilita acceso público, no modifica Firestore, no crea usuarios Firebase, no concede roles a nivel de proyecto ni activa CI/CD.**

### Paso 1: simulación
```bash
cd ~/SmartRoute_AI
git pull --ff-only
bash scripts/gcp-bootstrap-gateway-identity.sh
```

### Paso 2: ejecución explícita por el propietario
```bash
CONFIRM_SMARTROUTE_GATEWAY_IDENTITY=proyectopersonal-480420/smartroute-api-staging \
  bash scripts/gcp-bootstrap-gateway-identity.sh
```
Puede fallar si la identidad de Cloud Shell no dispone de permisos para crear cuentas o modificar políticas IAM del servicio. Si ocurre, **no ampliar permisos indiscriminadamente**; diagnosticar permiso exacto.

## Pendiente de fases posteriores
- Revisar mecanismos de limitación de abuso y costos para una entrada pública y el alta del usuario de prueba.
- Desplegar inicialmente servicio de gateway **privado**, verificar WIF/Cloud Run IAM service-to-service, salud y rechazos por Firebase token inválido.
- Diseñar/autorizar apertura limitada de entrada Firebase-authenticated a Android/web, orígenes web explícitos y observabilidad; ninguna acción pública hasta aprobación del propietario.
- Ejecutar prueba real del token Firebase del usuario, rol `OPERATOR` en `users/{uid}` de Firestore `smartroute`, solicitudes de órdenes/rutas y limpieza.
- Mantener `GCP_STAGING_ENABLED=false`.
