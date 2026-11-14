# Decisiones para la demo web-first de SmartRoute AI

**2026-11-14 · Propuestas de ADR-13 y ADR-14 para revisión**, complementarias a ADR-01–12. No sustituir en silencio los entregables históricos.

## ADR-13 — Cartografía y matriz vial de bajo costo

- **Decisión piloto:** React + Leaflet con teselas basadas en datos OpenStreetMap; `openrouteservice` como proveedor de duración/distancia por vías reales y OR-Tools como solucionador.
- **Alternativas:** Google Maps Routes API (diseño inicial); OSRM propio; distancias euclidianas.
- **Justificación:** facilitar demo académica real sin asumir facturación de Google Routes API por cada matriz.
- **Consecuencias:** key ORS en Secret Manager solo backend, límites de cuotas del proveedor, atribución visible y política de teselas, matriz acotada a depósito + 10 paradas, adaptador sustituible para futuro Google Routes API.
- **Precaución:** las rutas de calle y tiempos son estimados, no medición del piloto. Un mapa basado en OSM no garantiza cartografía gratuita ilimitada ni SLA.
- **Aceptación:** backend entrega misma lista de pedidos sin duplicaciones; matriz inválida devuelve 422, proveedor inaccesible 503, resultado conserva huella/procedencia, la geometría de recorrido es opcional.

## ADR-14 — Secuencia de ingeniería web-first

- **Decisión:** web del operador y rutas optimizadas primero, luego Flutter Android.
- **Objetivo:** demostrar alto valor del producto con un vertical slice real: Google Sign-In → pedidos → mapa → matriz vial → OR-Tools → comparación → guardar/publicar ruta (fase posterior) → app DRIVER.
- **Impacto SDD:** reordenar US-003/004/005 y US-009/010 antes de US-006/007/008 sin eliminar historias P0; actualizar cronograma del siguiente incremento.
- **Restricciones:** API privada tras gateway; protección IAM/Firebase; Firestore exclusiva `smartroute`; Geminin consultivo sigue P1.
- **Entrega de este PR:** frontend de operador, listado/alta de pedidos y endpoint de **previsualización** autenticada, sin publicación de ruta. La función de crear/publicar rutas se incorpora en la siguiente historia.
- **No se afirma:** ahorro observado, optimización óptima global, acceso real a la API ORS ni despliegue GCP antes de ejecutar tests E2E.

[OpenStreetMap policy](https://operations.osmfoundation.org/policies/tiles/) · [HeiGIT API docs](https://playground.heigit.org/) · [ADR vigentes](ADR.md).
