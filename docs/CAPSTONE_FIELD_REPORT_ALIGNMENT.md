# Alineación con Informe de Práctica de Campo I (UPN 2026-2)
Documento de 50 páginas facilitado por el equipo, usado como referencia funcional. Mantener fuente original bajo custodia de autores; esta ficha recoge decisiones y hallazgos relevantes sin presentarlos como validados por empresa externa.

## Hechos del informe
- Título: «SmartRoute AI: aplicación móvil de logística de última milla con optimización de rutas para reducir el tiempo de entrega en una empresa de reparto de Lima Metropolitana, 2026».
- Equipo de cuatro autores (25 % cada uno). Proyecto académico de caso ficticio.
- OE1: tiempo promedio -20%; OE2: distancia menor; OE3: puntualidad mayor.
- Investigación aplicada/cuasi-experimental: 30 recorridos planeados, 15 A (manual) + 15 B (optimizados); 5–10 paradas; mismo depósito y condiciones comparables.
- Simulación previa documental: 30 recorridos, 233 entregas, registros 23.31 min, vecino 16.13 min, OR-Tools 15.02 min por entrega. No evidencia de mejora observada.
- 5 necesidades NEC-01…05, 5 causas raíz CR1…CR5, Pareto documental, Ishikawa, cinco porqués, 3 alternativas con puntajes A3=4.10, A2=3.50, A1=3.10 (matriz elaborada en informe).
- Diseño: Flutter, React, FastAPI/Cloud Run, PostgreSQL, Google Routes, OR-Tools, Gemini read-only.
- Informe reconoce apartados aún en plantilla: calidad SQA, metodología, pruebas, despliegue, indicadores reales y ética individual; no registrar como finalizados.
- La simulación utiliza tiempos aproximados, no matriz Routes API observada. Debe tratarse como escenario inicial de contraste, no evidencia de operacionalización real.

## Correcciones/pendientes críticos para cerrar
1. Recoger evidencia primaria del problema o confirmar aceptación docente del caso sintético.
2. Validar 3 expertos y confiabilidad de instrumentos, si se llevará a cabo, sin inventar puntuaciones.
3. Verificar precios de GCP y fuentes legales al día; la estimación del informe no implica precio contratado.
4. Fijar definición coherente de tiempo de entrega (duración total ruta / entregas completadas) y registrar servicio por parada, ventanas y muestras.
5. Adjuntar sim_baseline.py y bc.py solo tras revisión de licencia/fuentes, reproducibilidad, semillas y versión; no se presupone que están en GitHub.
6. Ejecutar pruebas AC-001…016 y registrar salida antes de marcar requisitos como validados.
7. Capturar resultados reales del piloto (si existe) y diferenciar de datos sintéticos.
8. Elaborar documento final con informe original, matrices de riesgo/ética, pruebas, video y material OneDrive institucional.
