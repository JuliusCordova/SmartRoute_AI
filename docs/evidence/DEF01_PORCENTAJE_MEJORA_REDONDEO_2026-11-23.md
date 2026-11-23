# DEF-01 — Reconciliación de porcentajes de mejora y redondeo

**Fecha:** 23/11/2026. **Fuente:** informe final entregado 22/11, tabla 98, defectos y tabla 87 de puntos. Incidencia: el ejemplo del 15/11 muestra porcentaje de mejora **19,43 %**, mientras la comparación visual de **32 → 25 minutos redondeados** sugeriría ~21,9 %. Los dos cálculos no utilizan los mismos números de entrada.

## Causa de presentación identificada en código

`apps/operator-web/src/main.jsx` presenta tiempo con `mins(v) = Math.round(v/60)` (minutos enteros), pero usa `preview.improvement_pct` de la API para el porcentaje. `services/api/app/route_preview.py` calcula `round(100*(baseline_s-optimized_s)/baseline_s,2)`, con **duraciones exactas enteras en segundos de la misma matriz ORS**. Por tanto, **no es válido** volver a calcular el ahorro usando los minutos **ya redondeados**: la discrepancia visual no demuestra por sí sola error del algoritmo.

## Corrección del PR

- Mostrar **segundos exactos** junto a tiempos expresados en minutos redondeados, tanto en la comparación preliminar como la ruta guardada.
- Etiquetar el porcentaje como **«Mejora estimada de tiempo»**, no de kilómetros.
- Nota visible: los minutos se redondean para lectura, el porcentaje usa segundos exactos; resultado **estimado**, no medido.
- Prueba de regresión: matriz sintética con 150 segundos baseline y 55 segundos optimizados produce **63,33 %**, sin utilizar minutos redondeados.

## Prueba pendiente para cerrar DEF-01 históricamente

- [x] Fuente precisa del cálculo encontrada y documentada.
- [x] Propuesta de cambio en UI y caso unitario.
- [ ] Dos workflows CI y QA del PR en verde.
- [ ] **Capturar el JSON de respuesta original o nueva corrida reproducible del caso de 15/11**, conservar `baseline_seconds`, `optimized_seconds`, `improvement_pct`, `matrix_fingerprint`, proveedor/fecha y confirmar **19,43 %** con esos valores.
- [ ] Confirmar captura UI revisada y trazabilidad con acta, sin reabrir rutas QA COMPLETED.

**Estado:** corrección de presentación y test reproducible. La cifra histórica **19,43 % permanece no auditada a nivel de segundos exactos** hasta disponer del JSON; no declarar cierre formal de ese dato.

Ningún cambio de este PR escribe en Firestore ni hace despliegue a Cloud Run.
