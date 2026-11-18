# ADR-16 — App del repartidor nativa en Kotlin y Jetpack Compose

**Estado:** Propuesto (15/11/2026). Reemplaza a ADR-01 (Flutter) para la app del repartidor.

## Contexto

ADR-01 eligió Flutter. Al empezar la app, el equipo trabajó en Android Studio y domina mejor Kotlin. El piloto solo usa repartidores con Android, e iOS está fuera del alcance del Capstone.

## Decisión

Construir la app del repartidor como app Android nativa con Kotlin, Jetpack Compose y Material 3. Se mantiene la arquitectura hexagonal: dominio y puertos sin dependencias de Android, adaptadores para datos simulados y para el gateway. OpenStreetMap con osmdroid y Firebase Authentication con Google Sign-In.

## Consecuencias

- Positivas:
  - Una sola plataforma que el equipo domina.
  - SDK oficial de Firebase para Android.
  - Pruebas JUnit y de Compose integradas en Android Studio.
- Negativas: no hay app iOS. Si se necesitara, habría que reescribir la UI; el dominio se podría portar a Kotlin Multiplatform.
- Documentos por actualizar: el informe (5.5, 5.7, 6.x y el stack), la presentación (stack y arquitectura) y la referencia a ADR-01.
