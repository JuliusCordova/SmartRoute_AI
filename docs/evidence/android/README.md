# Evidencias visuales Android — SmartRoute AI

**Corte:** 25/11/2026 · **Ambiente:** emulador Android (`emulator-5554`) · **Aplicación:** repartidor SmartRoute AI · **Alcance:** MVP académico.

## Capturas

1. [ANDROID_01_Mis_Rutas.png](ANDROID_01_Mis_Rutas.png): pantalla «Mis rutas», usuario autenticado, ruta `fb413b71...` completada, 5/5 paradas atendidas, 4 entregas realizadas y 1 no entregada, distancia 41,7 km y tiempo 61 minutos **estimados**.
2. [ANDROID_02_Detalle_Ruta.png](ANDROID_02_Detalle_Ruta.png): navegación al detalle de esa ruta, mapa OpenStreetMap, depósito, secuencia de cinco paradas y estados individuales. La línea del mapa conecta las paradas en orden, **no** debe interpretarse como trazado vial por calles.

## Trazabilidad técnica

- En Windows: `gradlew.bat :app:assembleDebug --no-daemon` terminó **BUILD SUCCESSFUL** en 53 segundos.
- APK debug: `app-debug.apk`, **33 070 890 bytes**, compilado el 24/11/2026 a las 22:04:49 (hora de la laptop).
- `adb -s emulator-5554 install -r app-debug.apk` terminó **Success**.
- Ejecución y navegación a detalle corroboradas por capturas de la sesión.
- La Release académica publicada utiliza el tag `Smart_route` y contiene el APK descargable: https://github.com/JuliusCordova/SmartRoute_AI/releases/tag/Smart_route

## Límites

Las imágenes documentan una ruta **ya completada**, no prueban transiciones de entrega activa, instalación en teléfono físico ni comportamiento offline. Los pedidos de prueba y las métricas son sintéticos/estimados. No confundir 100% de paradas atendidas con 100% de entregas exitosas.

## Referencias

- [Checkpoint Android y operador](../../checkpoints/CORTE_VISUAL_ANDROID_OPERADOR_DEF01_2026-11-24.md)
- [Acta de cierre del MVP académico](../../CIERRE_MVP_ACADEMICO_2026-11-25.md)
