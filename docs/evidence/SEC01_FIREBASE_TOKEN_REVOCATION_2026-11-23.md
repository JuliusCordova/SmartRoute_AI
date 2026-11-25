> **ADENDA 25/11/2026:** La validación controlada E2E del **Gateway en staging** se ejecutó después de este corte: cuenta QA `DRIVER`, solicitud inicial `GET /api/v1/orders?limit=50` con **HTTP 403** por RBAC, revocación Firebase confirmada a las 19:32:30 UTC, reenvío con token antiguo según procedimiento y **HTTP 401**. Ver [registro SEC-01 25/11](SEC01_REVOCACION_REAL_STAGING_2026-11-25.md). Las casillas pendientes de abajo son **históricas a 23/11**; permanecen fuera de esta prueba la medición de latencia/coste y una comprobación E2E separada del backend privado.\n\n# SEC-01 — Verificación de revocación Firebase en Gateway + API

**Fecha:** 23/11/2026 · **Alcance:** cambio de código y regresión automatizada; sin despliegue GCP.

## Problema confirmado

El informe de presentación (22/11, cap. 5.11 y tabla 72) identificó `check_revoked=False` en:
- `services/gateway/app/main.py` — el Gateway autenticaba ID tokens, pero no verificaba revocación.
- `services/api/app/auth.py` — la API privada también validaba firma/claims sin consultar revocación.

Un ID token Firebase aún dentro de su vigencia podría ser aceptado después de revocar las sesiones del usuario. Firebase Admin `verify_id_token(check_revoked=True)` valida estado de revocación y cuenta deshabilitada contra Firebase Authentication; requiere **una consulta adicional por verificación**.

## Corrección

1. Gateway: `auth.verify_id_token(..., check_revoked=True)`; tokens revocados/invalidos dan **401** y no generan token IAM hacia el Backend.
2. API: `auth.verify_id_token(..., check_revoked=True)`, captura explícita de `auth.InvalidIdTokenError` (incluye `RevokedIdTokenError`) y `auth.UserDisabledError` como **401**, sin revelar el token ni identidad. Otros fallos inesperados permanecen como **503 fail-closed** según contrato.
3. Pruebas nuevas: Gateway comprueba `check_revoked=True` en token válido y revocado, y ausencia de llamada IAM en rechazo. API verifica 401 para revocado/deshabilitado/inválido y rol tras autenticación positiva.

## Criterios de cierre y límites

- [x] Gate de revocación configurado en ambos puntos de control.
- [x] Pruebas unitarias con mocks agregadas sin llamadas reales a Firebase ni GCP.
- [ ] Workflows CI + QA Automation del PR deben estar en verde.
- [ ] Validación **staging** con usuario sintético: obtener ID token, verificar acceso, ejecutar **revocación consentida de tokens en cuenta QA**, repetir request con token antiguo → 401 en Gateway y/o API. **No ejecutada por este PR**; no revocar cuentas reales sin plan de recuperación.
- [ ] Medir impacto de latencia y coste en verificación de cada request; evitar disminuir requisitos RBAC o omitir verificación de revocación por conveniencia.
- [ ] Despliegue requiere gate/aprobación de cambio; el PR no cambia tráfico Cloud Run ni permisos IAM.

**Estado:** `CODE + UNIT TESTS IMPLEMENTED`; **no marcar SEC-01 como validado E2E/DEPLOYED** sin prueba de un token realmente revocado en ambiente controlado.

**Fuente de contrato:** [Firebase Admin Python — auth.verify_id_token](https://firebase.google.com/docs/reference/admin/python/firebase_admin.auth); [Firebase — Manage user sessions](https://firebase.google.com/docs/auth/admin/manage-sessions).
