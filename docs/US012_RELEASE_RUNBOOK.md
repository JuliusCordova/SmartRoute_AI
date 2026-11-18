# US-012 — Release gate y rollout controlado (staging)

**Estado:** procedimiento; no es evidencia de despliegue. La ruta de Manuel permanece PLANNED hasta una prueba autorizada por el usuario.

## Gates obligatorios previos a merge

1. PR #57 en HEAD actual con `api-tests`, `operator-web-build` y `firestore-emulator` satisfactorios.
2. API: comprobar las pruebas `test_us012_route_execution_api.py`, `test_us012_route_execution_repo.py`, compatibilidad de `OptimizedRoute` ACTIVE y regresión US-011.
3. Gateway: probar `OPTIONS /api/v1/driver/me/route/start` para orígenes permitidos (204) y no permitidos (403), y sin Firebase (401).
4. Confirmar que `services/api/app/firestore_config.py` apunta exclusivamente a proyecto aprobado y DB nombrada `smartroute`, nunca `(default)` ni `gestioncitas`.
5. Revisar semántica idempotente y emisión de `route_events` con una transacción en emulador.
6. Validar que el PR móvil #56 sigue separado y que la web OPERATOR es solo lectura respecto a activar recorridos.

## Secuencia de publicación (requiere verificación de resultados)

1. Merge PR #57 solo tras CI completo.
2. Construir imagen inmutable para **API** desde commit del merge (mismo patrón de Cloud Build existente). Desplegar revisión **sin tráfico** y comprobar `/health`, `/ready`, API 401 sin Firebase y contrato de estado ACTIVE. Promover API antes de habilitar el nuevo endpoint del gateway.
3. Construir/desplegar revisión **gateway** sin tráfico desde ese commit, conservando `SMARTROUTE_ALLOWED_ORIGINS` (dominio web principal, temporal US-011 y localhost), proyecto, backend, servicio IAM y `SMARTROUTE_GATEWAY_ENABLED=true`. Verificar 401 sin token, 204 OPTIONS válido, 403 origin inválido; después promover gateway.
4. Construir/desplegar **web OPERATOR** sin tráfico y verificar compilación, Firebase Authorized Domains y cargas de rutas existentes; promover tras smoke test. Mantener revisión previa para rollback.
5. Probar lectura DRIVER autenticada con identidad propia; **no ejecutar POST start** hasta contar con aprobación para cambiar la ruta piloto. Durante el test positivo, usar `expected_version` de Firestore y nueva clave UUID; exigir posterior estado `ACTIVE`, reserva `ACTIVE`, un único evento auditado y lectura web ACTIVE.

## Rollback

- Guardar los identificadores de revisión activos **inmediatamente antes** de cada promoción (`gcloud run services describe`).
- Volver a revisión previa con `gcloud run services update-traffic ... --to-revisions=OLD_REV=100`, componente por componente.
- No revertir manualmente estados operativos de Firestore durante rollback. Si una ruta ya está ACTIVE, una versión API anterior que solo admite PLANNED podría fallar al leerla; por eso **no iniciar rutas reales** antes de finalizar el gate de compatibilidad y plan de contingencia.
- No confundir rollback de código con reversión de datos; registrar evidencia de ambas verificaciones.

## Evidencia mínima de cierre

PR y SHA; resultados CI de SHA exacto; revisiones API/gateway/web; HTTP health/ready; autorizaciones 401/403 y preflight 204; captura web OPERATOR mostrando ACTIVE; respuesta DRIVER mostrando solo su ruta; comprobación de evento y estado reserva sin mostrar tokens; pruebas de rollback.
