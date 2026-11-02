# US-009 — Evaluación OR-Tools, primer slice autónomo sin costo GCP

**Estado esperado del PR:** implementación del módulo de solver + pruebas unitarias en CI. No integra aún Google Routes API, rutas persistidas ni endpoint Cloud Run.

## Objetivo y contrato
Validar una matriz de duraciones **sintética** para un depósito y de 1 a 10 paradas, calcular tiempo total de ruta original y secuencia recomendada con OR-Tools, y devolver IDs ordenados, tiempos, mejora calculada y hash SHA256 para reproducibilidad. Son retornos al depósito (ciclo), no una ruta abierta. Una matriz [n+1]×[n+1] está ordenada como [depósito, pedido 1, ...pedido n]. Acepta tiempos asimétricos y exige valores no negativos <= 86 400 segundos por tramo. No llama a Google Maps.

## Límites de evidencia
- OR-Tools usa estrategia PATH_CHEAPEST_ARC y una sola solución para consumo limitado; puede retornar ruta subóptima. **No afirmar optimalidad global**.
- Si el costo es superior al orden inicial se conserva la línea base.
- `data_origin=synthetic` obligatorio; la mejora no demuestra OE1 ni tiempos observados.
- No crear APIs públicas para subir matrices arbitrarias. Conectar a US-010 solo tras autorizar y probar el adaptador de Routes API con límites de cuota, persistencia e idempotencia.
- Conservar matrices solo como fixtures creados por nosotros; no almacenar respuestas brutas de Google Maps sin revisar licencias.

## Definition of Done
`python -m pytest -q tests/test_optimization.py` y CI Docker pasan, sin GCP. Pruebas cubren mejoras, repetición, tamaño, duplicados, diagonal e imposibilidad de fingir datos reales.

## Etapas siguientes
1. US-010: adaptador Google Routes API en Cloud Run con mocks y límites de 10 paradas, sin claves en GitHub.
2. Unir la salida con `routes/{routeId}` y `route_evaluations` en Firestore, con transacciones y verificación de autorización.
3. Comparar contra vecino cercano y orden original con mismo input, evitando sesgo en el piloto.
