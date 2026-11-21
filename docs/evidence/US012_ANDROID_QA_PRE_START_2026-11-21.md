# US-012 — Evidencia visual previa al inicio (2026-11-21)

## Contexto

- Proyecto: SmartRoute AI — Capstone UPN.
- Rama de QA: `feat/mobile-driver-android-base`.
- Captura original: `image(20261121-020911).png`, compartida en la conversación.
- Estado de la evidencia: **pantalla de detalle de ruta ANTES de pulsar «Iniciar recorrido»**. No constituye evidencia de una transición exitosa a `ACTIVE`.

## Observaciones verificables en la captura

- Android muestra «Ruta 21e3de4b…» y botón **Iniciar recorrido**.
- Mapa de OpenStreetMap con paradas numeradas, depósito y línea de unión entre puntos. La línea no representa el recorrido por calles.
- Indicador de progreso: **0 de 6 — 0 %**.
- Estado de paradas visibles: **Por entregar**.
- Métricas mostradas: **35.3 km, 56 min, dato estimado**.
- Primeras paradas visibles: Av. Angamos Oeste 980 (Miraflores), Av. del Ejército (Miraflores), Morro Solar 1160 (Chorrillos).

## Contexto de verificación independiente

La lectura Firestore realizada por el usuario antes de esta captura mostró:
- Ruta QA `21e3de4b-4002-5870-bc4e-8eafb2826219`: `PLANNED`, versión 2.
- Seis órdenes de la ruta QA: `ASSIGNED`.
- Ruta de Manuel `681f7f60-3a77-5f6b-975e-578fb03e4204`: `PLANNED`, versión 2.

Estos estados pertenecen a la comprobación anterior, no se deducen únicamente de la captura.

## Pendiente de cierre de QA

1. Adjuntar la captura original PNG al repositorio en `docs/evidence/screenshots/US012_ANDROID_QA_PRE_START_2026-11-21.png`; conservada en la conversación.
2. Ejecutar `start` una sola vez con identidad y ruta QA verificadas.
3. Verificar en Firestore `ACTIVE` / versión 3 / seis órdenes `IN_TRANSIT`.
4. Documentar evidencia posterior y completar US-013 y US-014.

**Seguridad:** mantener PR #56 sin merge y no operar sobre la ruta de Manuel.
