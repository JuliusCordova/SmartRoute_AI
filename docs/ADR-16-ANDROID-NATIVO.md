# ADR-16 — Android nativo para SmartRoute DRIVER

**Fecha de decisión:** 2026-11-15 (reconciliada 2026-11-21).  
**Estado vigente (2026-11-22):** Android Kotlin/Compose integrado a `main` por PR #60 (`44f9748`); piloto QA E2E validado para una ruta nueva. El PR #56 queda como rama histórica, no como bloqueo para la integración vigente.  
**Alcance:** Aplicación móvil DRIVER, Capstone UPN.

## Contexto

El diseño académico inicial planteaba Flutter. La implementación actual del prototipo funcional de conductor está escrita en **Kotlin + Jetpack Compose + Material 3**, usando Android Studio. La demostración piloto está delimitada a Android, no iOS.

## Decisión

Adoptar Android nativo para el rol DRIVER, con capas `domain`, `data`, `di` y `ui`; Firebase Authentication (Google Sign-In); llamadas HTTPS autenticadas al gateway Cloud Run; vistas de rutas y paradas; mapa OpenStreetMap mediante osmdroid. El cliente no accede directamente a Firestore ni a la API privada.

## Motivación

- Plataforma disponible y conocida por el equipo.
- SDK Firebase Android y ecosistema de pruebas JUnit/Compose.
- Menor alcance que una implementación multiplataforma para este piloto académico.

## Evidencia y límites

- CI QA #6: 42 pruebas Android aprobadas y compilación debug exitosa, descritas en [evidencia QA](evidence/QA_AUTOMATION_RUN_6_2026-11-20.md).
- Prueba controlada de inicio, registro de 5 entregas y 1 incidencia, cierre de ruta `COMPLETED` y persistencia: [evidencia US-012 a US-014](evidence/US012_US013_US014_QA_FINAL_PASS_2026-11-21.md).
- Los servicios Cloud Run US-014 usados en las pruebas están etiquetados con 0 % del tráfico principal; no inferir de ello promoción a producción.
- **No** se implementa compatibilidad iOS ni se acredita navegación giro a giro o seguimiento GPS productivo.
- El código está integrado en `main` con `ENABLE_QA_WRITE_TEST=false`. La prueba de escritura sobre la ruta `aec305db...` se habilitó únicamente en un build **local DEBUG**; no promover ese ajuste local ni distribuir ese APK como versión general.

## Consecuencias para la entrega UPN

Actualizar el stack de la memoria, diagramas, SDD y presentación: referencias a Flutter son histórico de diseño, no descripción de la app entregada. Diferenciar estimaciones de optimización de tiempos operativos observados.

## Registro de control

Este ADR documenta la decisión; el flujo QA del 22/11 se ejecutó mediante despliegues etiquetados sin tráfico principal. Consultar [acta E2E](evidence/E2E_OPERADOR_ANDROID_QA_2026-11-22.md).
