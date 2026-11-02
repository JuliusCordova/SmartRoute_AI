# Recuperación de bootstrap staging tras fallo de red en docker push

## Evidencia
Cloud Shell del usuario confirmó que `smartroute-staging` fue **creado** y Docker terminó compilación satisfactoriamente. El push falló con `connect: connection refused` hacia `us-central1-docker.pkg.dev:443`. Cloud Run aún **no** fue creado porque el script se interrumpió antes de invocar `gcloud run deploy`.

## Recuperación con imagen local ya construida
En la misma sesión de Cloud Shell donde se compiló la imagen:
```bash
cd ~/SmartRoute_AI
git pull --ff-only
SMARTROUTE_IMAGE_SHA=da8df041d240f0868488741116f913d57e0a0d6d bash scripts/gcp-recover-staging-push.sh
```
El comando anterior es un **dry run** y exige que Docker aún conserve la imagen local.

La ejecución autorizada para completar exactamente el bootstrap inicial es:
```bash
CONFIRM_SMARTROUTE_RECOVERY=proyectopersonal-480420/smartroute-api-staging \
  SMARTROUTE_IMAGE_SHA=da8df041d240f0868488741116f913d57e0a0d6d \
  bash scripts/gcp-recover-staging-push.sh
```

El script no reconstruye ni modifica las bases Firestore, permisos IAM ni proyectos ajenos. Verifica que la base de imágenes y la imagen local existan; reintenta `docker push` cuatro veces y, solo tras éxito, crea el servicio Cloud Run **privado** previamente autorizado con límite 0-2 instancias y cuenta `smartroute-runtime`. Se detiene si el servicio ya existe.

Si Docker local no tiene imagen o Cloud Shell cambió de instancia, no ejecutar a ciegas. Recompilar con un plan nuevo si hace falta. Si la red sigue rechazando conexiones a :443, revisar conectividad de Cloud Shell o usar un mecanismo alternativo de compilación aprobado. GitHub staging sigue desactivado.
