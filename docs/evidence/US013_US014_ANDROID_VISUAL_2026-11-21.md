# US-013 / US-014 — Evidencia visual Android (2026-11-21)

## Evidencia aportada

Capturas compartidas en la conversación del Capstone SmartRoute AI, recorrido QA `21e3de4b-4002-5870-bc4e-8eafb2826219`.

1. **US-013:** pantalla de ruta con `6 de 6 · 100 %`, cinco órdenes en «Entregado» y última en «No entregado». Botón «Finalizar recorrido» visible.
2. **US-014 (confirmación):** diálogo «¿Finalizar recorrido?» donde Android indica que GCP confirmará el cierre y liberará la reserva.
3. **US-014 (resultado):** pantalla posterior con texto «Recorrido completado: 5 entregadas y 1 fallidas», `6 de 6 · 100 %`, sin botón de finalización.

## Límites de la evidencia

Las capturas demuestran el comportamiento visual de Android, no prueban por sí mismas el estado persistido ni que la reserva se haya liberado. La comprobación independiente de Firestore queda **PENDIENTE**. No marcar US-014 como PASS de base de datos hasta revisar `routes`, `orders`, `driver_assignments` y ruta de Manuel.

Archivos fuente de las capturas aportados al chat: `image(20261121-022133).png`, `image(20261121-022235).png` y `image(20261121-022250).png`. PNG originales aún no incluidos en este commit.

## Estado del proyecto

- Rama `feat/mobile-driver-android-base`, PR #56 pendiente de merge.
- Revisión de pruebas US-014 aislada del 100 % del tráfico principal.
- No hacer nuevas mutaciones ni repetir cierre antes de verificación Firestore.
