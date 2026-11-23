# US-016 — Evidencia automatizada del backend público protegido

Corte: 23/11/2026. **Sin despliegue a GCP y sin habilitar servicio público**.

## Fuente verificable (commit `c7133e32bfd1236344d26d2ba6ffddc7af6d59f3`)

- CI: https://github.com/JuliusCordova/SmartRoute_AI/actions/runs/45262357897
  - api-tests: **PASS**, 106 aprobadas, 11 omitidas.
  - gateway suite ejecutada en CI: **PASS**, 34 aprobadas.
  - firestore-emulator: **PASS**.
  - operator-web-build: **PASS**.
  - deploy-staging: **SKIPPED** (PR, sin despliegue).
- QA: https://github.com/JuliusCordova/SmartRoute_AI/actions/runs/45262357946
  - Gateway auth + routing: **PASS**.
  - Backend + Firestore Emulator: **PASS**, 116 aprobadas y 1 omitida.
  - Operator React build: **PASS**.
  - Android: comprobar resultado independiente al cierre del workflow.
- Frontend cliente en PR #81, commit `aa7e3acad11c5c5c02945309898eb6932ba0ab8c`:
  - job `customer-tracking-tests`, 6/6 PASS:
    https://github.com/JuliusCordova/SmartRoute_AI/actions/runs/45262171992

## Incidencias detectadas y corregidas por pruebas

1. Un test de gateway simulaba Firebase sin rechazo después de la llamada pública; se aisló el mock y se comprobó que una ruta privada sigue exigiendo Firebase.
2. Cuando la función pública estaba desactivada, la dependencia creaba Firestore antes de bloquear el acceso; corregido con verificación previa del feature gate.

## Validación de seguridad cubierta por tests

- Token fuerte de 256 bits; solo SHA-256 persistido.
- Un token solo resuelve el pedido asociado; test con dos pedidos sintéticos.
- Estados inválidos, enlace revocado y expirado rechazados.
- Solo OPERATOR puede emitir o revocar links.
- La vista del cliente no incluye GPS, driver_id, direcciones de otros pedidos, ruta completa ni datos personales.
- Gate opt-in en Gateway y API; 404 con gate desactivado.
- Token enviado por POST JSON; frontend recomendado `/#/t/{token}` para evitar que la ruta HTTP registre el secreto.

## Gates aún sin cerrar

- Ensayo E2E con dos pedidos sintéticos A y B en revisión QA aislada.
- Gestión de límite de tasa perimetral (Cloud Armor o equivalente), no habilitar enlace público sin ella.
- Verificar que no se registren request bodies/token, métricas de errores y políticas CORS/referrer/no-store.
- Prueba visual en navegador móvil, generación del link por operador y revocación E2E.
- Validar compatibilidad con Android y captura de UI comparada con prototipo.
- No fusionar ni habilitar el feature gate hasta decisión del responsable y evidencias de staging.
