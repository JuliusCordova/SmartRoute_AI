# CR-2026-11-24-02 — US-012 y US-015 pasan a mejoras futuras

**Fecha:** 24/11/2026. **Motivo:** duración del curso Capstone de solo **7 semanas**. **Aprobado por:** responsable del proyecto.

## Decisión vigente

| Historia | Puntos históricos | Estado en la entrega de noviembre | Destino |
| --- | ---: | --- | --- |
| US-V1-012: asistente consultivo Gemini | 5 | **FUERA DE ALCANCE** | **MEJORA FUTURA** |
| US-V1-015: piloto comparativo en campo y exportación | 5 | **FUERA DE ALCANCE** | **MEJORA FUTURA** |

El curso de siete semanas no permite implementar y evaluar adecuadamente el asistente Gemini ni organizar y ejecutar un piloto comparativo de campo con línea base y mediciones observadas. **No son historias fallidas ni atrasadas: son mejoras futuras, no comprometidas para esta entrega.**

Esta decisión **reemplaza** las disposiciones de CR-2026-11-23-01 que mantenían Gemini en P1 pendiente y conservaban el piloto. Siguen excluidos de esta entrega: offline/cola local US-013/014, deshacer entrega, semáforo de puntualidad y exportación.

## Alcance que permanece

Web de operador, Android del repartidor, web de seguimiento del cliente US-016, API, gateway, Firestore, rutas optimizadas OR-Tools, mapas, seguridad y evidencias técnicas. Se conserva la comparación **estimada** de secuencia base frente a optimizada y KPI del software (US-009/011). Esa comparación **no equivale** al piloto real US-015.

No presentar simulaciones o pruebas QA como ahorro, puntualidad o mejora **observados en campo**.

## Backlog y medición

- Base histórica académica: **71 puntos**.
- Fuera del alcance de esta entrega: US-013/014 (**8 puntos**), US-012 (**5**), US-015 (**5**): **18 puntos**.
- Denominador nominal ajustado: **53 puntos**, condicionado a reconciliar criterios y pesos. **No publicar porcentaje nuevo** hasta validar numerador de historias retenidas.
- Historias US-012 y US-015 deben figurar bajo **Mejoras futuras**, no bajo **Pendientes para el viernes**.
- Los documentos e informes académicos ya presentados no se reescriben retroactivamente: esta adenda registra el cambio para la versión final.

## Mejoras futuras propuestas

**US-012:** asistente Gemini consultivo con evaluación de respuestas, privacidad, guardrails y presupuesto de inferencia.

**US-015:** diseño de protocolo, muestra, ejecución de piloto comparativo real, métricas observadas de tiempo/distancia/puntualidad, análisis de resultados y exportación según se justifique.

## Prioridades de entrega antes del sábado 28/11

1. Ajustes visuales del operador conforme a prototipos, sin eliminar funcionalidades.
2. Cierre Android y evidencias.
3. Consolidación US-016, integración, documentación y entrega.

**Cambios limitados a documentación/backlog; sin tocar main, ni desplegar infraestructura.**
