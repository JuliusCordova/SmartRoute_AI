# US-011 — Visualización de indicadores del operador (incremento 1)

**Fecha:** 23/11/2026 · **Alcance:** panel React y lógica pura en JavaScript. **Sin mutaciones de Firestore, sin nuevas rutas, sin cambios de API/GCP.**

## Requisito

Acercar la experiencia del operador a los prototipos del informe UPN (comparación de rutas, Fig. 16) sin eliminar las funcionalidades existentes: pedidos, filtros, búsqueda, CRUD de centros, geocodificación, mapa OSM, optimización OR-Tools, persistencia, asignación, GPS en ruta activa y panel ejecutivo.

### Recorte de alcance aprobado

[CR-2026-11-23-01](../decisions/CR-2026-11-23-01_RECORTE_ALCANCE_MVP.md): sin deshacer entrega, semáforo de puntualidad, offline ni exportación de resultados. El piloto comparativo permanece para sustentar resultados.

## Entrega técnica

1. `apps/operator-web/src/operations.js`: **projectRouteIndicators(routes)** proyecta por ruta tiempo y distancia baseline/optimizada, diferencias de porcentajes con denominadores exactos, validación de números y fuente `estimated`. No infiere tiempos observados ni puntualidad.
2. `apps/operator-web/src/main.jsx`: nueva tabla accesible de indicadores por ruta integrada en el dashboard existente, respetando filtro de estados y paginación parcial. Muestra segundos exactos, minutos redondeados y los kilómetros.
3. `apps/operator-web/src/style.css`: estilo de tabla y tarjetas en paleta navy/amarillo del prototipo, responsivo con scroll horizontal y sin sobrescribir estilos existentes.
4. `apps/operator-web/tests/operations.test.js`: tres pruebas para valores exactos, ausencia de telemetría falsa y proyección no mutante.

## Verificaciones

- [x] Cambios aislados al frontend y tests de lógica.
- [ ] CI y QA Automation del PR en verde; comprobar los dos resultados tras apertura de PR.
- [ ] Captura UI en el navegador conectado al entorno QA (visual de referencia) aún pendiente. No afirmar prueba manual de pixel-parity.
- [ ] US-011 completa: falta establecer criterios y evidencias de tiempos **observados**; el proyecto no dispone de mediciones físicas comparables en la ruta QA emulada.

**Criterio de honestidad:** las mejoras mostradas siguen siendo cálculos de optimización con ORS; no se han observado recorridos reales. No se presenta semáforo de puntualidad ni exportación. La ausencia de métricas se expresa como «—» o «Sin dato», nunca como 0 % calculado.
