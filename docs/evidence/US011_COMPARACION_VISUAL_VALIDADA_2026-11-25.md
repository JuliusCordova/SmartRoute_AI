# US-011 — Aceptación visual de comparación de rutas

**Fecha:** 25/11/2026. **Ambiente:** SmartRoute AI, operador web en Cloud Run staging. **Repositorio:** `JuliusCordova/SmartRoute_AI`. **Estado:** **Validación visual aceptada**.

## Evidencia observada

Durante revisión del panel web, el usuario proporcionó una captura de la vista previa de optimización con dos trazados simultáneos sobre OpenStreetMap en Lima:

- **Ruta base:** trazo gris discontinuo, conectores de secuencia **esquemática**.
- **Ruta optimizada:** trazo naranja, representación de recorrido vial **estimado**.
- **Leyenda superior:** «Base · secuencia esquemática» y «Optimizada · vial estimada».
- **Leyenda inferior:** «Comparación base vs. optimizada · ambas secuencias estimadas».
- La sección `03 · Comparación` indicó estado `ESTIMADO` en la captura.

**Resultado:** se confirma visualmente la superposición de ambas representaciones y la diferenciación explícita de sus fuentes/alcance. La validación se realizó en una **vista previa**, sin necesidad de guardar ni asignar una nueva ruta.

## Regla funcional corroborada

En `apps/operator-web/src/main.jsx` las casillas de selección de pedidos para optimización se deshabilitan cuando `o.status !== "PENDING"`. Por tanto, los pedidos `ASSIGNED` no se pueden seleccionar para construir una nueva ruta; esto es comportamiento esperado, no un fallo de la interfaz. El usuario corroboró esta distinción durante la sesión.

## Alcances y límites

- **US-011 comparación visual de dos rutas: validada mediante captura en la conversación.**
- La captura binaria **no está adjunta como archivo de imagen al repositorio** por medio de este commit; este documento conserva la descripción verificable de lo observado.
- El trazado base es **esquemático** y el optimizado **estimado**; no representa evidencia de tiempos, distancias ni ahorro observados en campo.
- No se exige reabrir rutas `COMPLETED`, crear pedidos adicionales ni persistir otra ruta para cerrar esta comprobación visual.
- **SEC-01** (token Firebase realmente revocado en staging) permanece como control pendiente separado.

## Relación con el cierre académico

Complementa `docs/CIERRE_MVP_ACADEMICO_2026-11-25.md` y sustituye exclusivamente el estado de aceptación visual que allí figuraba como pendiente. No altera otros límites de la entrega.
