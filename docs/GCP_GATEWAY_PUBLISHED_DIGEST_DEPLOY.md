# Primer despliegue privado del gateway desde digest publicado en GitHub

**Evidencia verificada:** GitHub Actions workflow run [41762609116](https://github.com/JuliusCordova/SmartRoute_AI/actions/runs/41762609116), job `126353548154`, conclusion `success`. El log de `docker push` confirma:

- Imagen `us-central1-docker.pkg.dev/proyectopersonal-480420/smartroute-staging/smartroute-gateway`
- Commit de publicación `02bc8c145761cfa4a5e37243f238367f571c096e`
- Digest publicado `sha256:d5c6abe6d73fd8b1ee4b0a8364ad89fb10799c67cc063c1b8f72826397c8ab47`

Se supera el bloqueo de conexión TCP de Docker en Cloud Shell **sin** usar Cloud Build ni ampliar roles de proyecto.

## Ejecución de propietario: simulación
```bash
cd ~/SmartRoute_AI
git pull --ff-only
bash scripts/gcp-deploy-published-gateway-private.sh
```
Valida proyecto y repositorio, existencia del digest, cuenta `smartroute-gateway`, backend privado y `roles/run.invoker` sobre ese backend; aborta si existe el gateway. Termina `DRY RUN: no Cloud Run service created.`.

## Ejecución autorizada: nuevo servicio PRIVADO
```bash
CONFIRM_SMARTROUTE_PUBLISHED_GATEWAY_DEPLOY=proyectopersonal-480420/smartroute-gateway-staging \
  bash scripts/gcp-deploy-published-gateway-private.sh
```

No hay `docker build` ni `docker push`. Crea exclusivamente `smartroute-gateway-staging` en `us-central1` con digest inmutable, SA dedicada, IAM privada, ingreso `all` pero **sin invocación no autenticada**, min 0/max 1, 1 CPU/512Mi y variables ancladas al backend privado. Verifica identidad y ausencia de `allUsers` y `allAuthenticatedUsers` en la política IAM directa. No cambia IAM, Firebase, Firestore, otros Cloud Run ni `GCP_STAGING_ENABLED=false`.

**Atención:** aunque IAM impide la invocación pública, `ingress=all` no bloquea el acceso de red: es una ruta disponible que requiere invocación IAM. No afirmar acceso privado de red/VPC. Existe riesgo de cargos por Cloud Run y Artifact Registry; max 1 instancia no es tope económico.

## Validación siguiente
Probar `/health` usando identidad IAM explícitamente autorizada para el nuevo gateway, sin abrir Cloud Run. Luego cubrir negativos de token Firebase y flujo OPERATOR real, antes de evaluar acceso Android/web y sus defensas antiabuso. No modificar proveedores o dominios Firebase del proyecto compartido.
