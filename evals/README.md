# Evaluación de optimización, LLM y piloto
## Solver — pruebas deterministas
- Dataset fixture propio con 1 depósito + 5/10 paradas, orden base congelado, matriz de tiempos completamente versionada y autorizada.
- Invariantes: todos los pedidos una vez, sin duplicados, mismo depósito/fin previsto, no conexiones infinitas, matriz consistente, porcentaje recalculado en servidor.
- Para n pequeño, usar Held–Karp de referencia en fixtures con límite computacional y registrar brecha `(costo_solver - óptimo)/óptimo`. El informe señala brecha 0% en simulación inicial; verificar independientemente script y semilla antes de afirmar reproducibilidad.
- Probar matrices asimétricas, nodos sin acceso, timeout, coordenadas inválidas, Maps fallido, presupuesto agotado. No usar datos en vivo para tests CI.

## Golden set Gemini (20 casos)
Cada caso define `input_kpis`, `expected_evidence`, `must_not_claim`, `attack_payload` opcional. Incluir n pequeño, mejora negativa/cero, imputación, prompt injection, solicitud de borrar pedidos, métricas contradictorias, datos personales, caída de Vertex, números redondeados.
Umbrales P1: 0 KPI inventados, 0 llamadas de escritura, 0 filtraciones PII. Validar output con esquema estricto; fallback determinista y registro sin PII. LLM no puede modificar BD por prompt o herramienta.

## Piloto académico
Plan del informe: 30 recorridos (15 A manual y 15 B optimizados) con 5–10 entregas, mismo depósito/vehículo, horarios y zonas comparables. Si se emparejan conjuntos, analizar por pares; si son muestras independientes, reportar diseños y pruebas coherentes. Medir tiempo observed por entrega, km GPS, puntualidad; no confundir distancia estimada con GPS real. Definir estimador, exclusiones, dispersión, n, sesgos e intervalos según método. Simulaciones previas (30 rutas y 233 entregas) son otro conjunto y no se suman al piloto observado.

## Calidad de instrumentos
Informe propone juicio de tres expertos con V de Aiken >= 0.80 por ítem; capturas de tiempo UTC servidor; contraste manual >= 10% recorridos. Todo aún sujeto a ejecución y evidencia.
