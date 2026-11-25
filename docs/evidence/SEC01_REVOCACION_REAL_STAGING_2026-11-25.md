# SEC-01 — Prueba controlada de revocación Firebase en staging

**Fecha:** 25/11/2026 · **Proyecto:** SmartRoute AI Capstone UPN · **Ambiente:** GCP `proyectopersonal-480420`, Firestore `smartroute`, Gateway Cloud Run staging.

## Contexto y cuenta de prueba

- Cuenta de QA de acceso controlado: `juliuscordova.jccd@gmail.com`.
- Firebase UID: `zMuwbYHLfST2QNdNkfosoCbUZ003`.
- Verificada con Firebase Admin: existe y está **habilitada**.
- Perfil en `users/{uid}`: `role=DRIVER`, `active=true`.
- El acceso a `GET /api/v1/orders?limit=50` requiere `OPERATOR`; un token autenticado con rol `DRIVER` debe recibir **403** antes de revocarse.

## Secuencia observada

1. En Chrome incógnito, cuenta QA autenticada. El Gateway aceptó una solicitud `GET /api/v1/orders?limit=50` con encabezado `Authorization: Bearer` y respondió **HTTP 403**, coherente con la restricción RBAC `Operator role required`.
2. Desde Cloud Shell se ejecutó `firebase_admin.auth.revoke_refresh_tokens(uid)` **únicamente** para la cuenta QA, sin deshabilitarla, borrar datos o cambiar el rol.
3. Consulta posterior `auth.get_user(uid)`: `tokens_valid_after_timestamp=2026-11-25T19:32:30+00:00` (**14:32:30 hora Perú**) y `disabled=False`.
4. Según el procedimiento guiado, se copió el token de la solicitud **GET original**, anterior a la revocación, sin publicar el valor en la conversación. Se introdujo de forma oculta con `read -s` en Cloud Shell; se envió por `curl --config -` al mismo endpoint del Gateway:
   `https://smartroute-gateway-staging-913797829604.us-central1.run.app/api/v1/orders?limit=50`.
5. La salida compartida fue **`HTTP_STATUS=401`**. La variable de shell que contenía el token se eliminó al terminar. No se grabó ni se incluyó el token en GitHub.

## Resultado y criterio

**Resultado de aceptación del flujo QA: SATISFACTORIO.** Se observó **403 antes** de revocar (identidad reconocida, rol no autorizado) y **401 después** al reutilizar el token original, con revocación registrada en Firebase para ese usuario. Esto respalda el control `check_revoked=True` implementado en `services/gateway/app/main.py` y `services/api/app/auth.py` y cubierto por pruebas unitarias anteriores.

**Límites de evidencia:** no se conservaron el token ni el hash del token para demostrar criptográficamente que ambas solicitudes usaron los mismos bytes. La conclusión se basa en la trazabilidad del procedimiento ejecutado y en los códigos HTTP observados; un HTTP 401 aislado también sería compatible con credenciales incorrectas. La verificación E2E directa fue del **Gateway**; no se hizo prueba diferencial adicional para el backend privado (Cloud Run IAM). No hay medición de latencia/coste de `check_revoked=True`.

## Notas de seguridad

- No volver a pegar ni publicar credenciales en chats, capturas, repositorios o logs.
- La revocación afecta los refresh tokens de esa cuenta QA; nuevas sesiones requieren autenticación.
- No se cambió IAM, roles de usuario ni tráfico Cloud Run.
- Evidencias de capturas y salida HTTP se observaron en la conversación; **archivos binarios de capturas no fueron añadidos a este commit**.

## Documentación relacionada

- `docs/evidence/SEC01_FIREBASE_TOKEN_REVOCATION_2026-11-23.md`: implementación y pruebas unitarias, corte previo al ensayo real.
- `docs/CIERRE_MVP_ACADEMICO_2026-11-25.md`: acta con estado histórico previo a esta prueba.
