# SmartRoute AI — Checkpoint Android US-011 / US-012 (18–19 nov 2026)

**Registro de avance documentado, no cierre de historia de usuario ni aprobación de producción.**

La implementación Android Kotlin + Compose, integración Firebase, contrato US-012 y sus pruebas están en la rama `feat/mobile-driver-android-base`, **PR #56 en borrador**, **sin merge** a `main`.

**Registro completo de evidencias:** [US012_ANDROID_FIREBASE_STAGING_2026-11-18.md](https://github.com/JuliusCordova/SmartRoute_AI/blob/feat/mobile-driver-android-base/docs/evidence/US012_ANDROID_FIREBASE_STAGING_2026-11-18.md)  
**PR:** https://github.com/JuliusCordova/SmartRoute_AI/pull/56

## Validado

- Android importado y compilado en Windows; pruebas JVM ejecutadas con `BUILD SUCCESSFUL`.
- Firebase Android registrado; Google Sign-In y consulta autenticada DRIVER de seis entregas demostrados en emulador.
- OpenStreetMap visible en emulador; línea une puntos, no representa ruta vial.
- API backend en rama: **57 passed, 9 skipped, 1 warning**.
- API de prueba `smartroute-api-staging-00012-gac` y gateway de prueba `smartroute-gateway-staging-00013-sov`: **0 %** de tráfico principal cada uno, verificaciones `/health` 200, API `/ready` 200, consulta sin Firebase 401.
- API principal `00010-juz` y gateway principal `00011-quj`: **100 %** de tráfico principal en las verificaciones.
- Lectura de Firestore `smartroute`: ruta piloto `681f7f60-3a77-5f6b-975e-578fb03e4204` **PLANNED, version=2, OPTIMIZED, 6 paradas**.
- Captura visual final: Android muestra diálogo **¿Iniciar este recorrido?** con **Cancelar** / **Confirmar inicio**. **No se ejecutó la transición POST.**

## Pendientes

Probar inicio transaccional `PLANNED → ACTIVE` con un **conductor y ruta sintéticos independientes**, verificar contrato autenticado y eventos/idempotencia; completar US-013, pruebas omitidas e integración/monitoreo. No promover gateway temporal al tráfico principal: está fijado a una URL de API etiquetada de pruebas.

**Punto de reanudación: paso 264**, lectura de `drivers` y `driver_assignments` en Firestore para seleccionar escenario aislado, sin tocar la ruta de Manuel.

Las capturas compartidas están descritas en el registro detallado, **no adjuntas como archivos PNG al repositorio**. Estimación no oficial de avance funcional: ~80 %.
