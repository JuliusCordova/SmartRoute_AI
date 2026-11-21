# SmartRoute AI — Corte académico y técnico para entrega del 22-11-2026

**Preparado:** 2026-11-21 (America/Lima)  
**Proyecto:** Capstone UPN — SmartRoute AI  
**Repositorio:** `JuliusCordova/SmartRoute_AI`  
**Rama de evidencia:** `feat/mobile-driver-android-base` · [PR #56](https://github.com/JuliusCordova/SmartRoute_AI/pull/56) **abierto, sin merge**

> **Alcance del corte.** Informe de avance demostrable, no reporte de implementación terminada, aceptación académica formal, ahorro observado ni certificación de seguridad en producción.

## 1. Resumen ejecutivo

SmartRoute AI implementa una solución académica de última milla con operador React, autenticación Firebase, gateway y API FastAPI en Google Cloud Run, persistencia aislada en Firestore `smartroute`, optimización OR-Tools sobre matriz vial estimada y aplicación Android Kotlin/Compose para el conductor.

**Avance global estimado:** ~65 % como apreciación gerencial, **no** porcentaje de cumplimiento de rúbrica ni conteo de historias P0 aceptadas. Existe evidencia del flujo de operador (cinco órdenes, cálculo de optimización) y del flujo de conductor QA (seis paradas, cinco entregas exitosas, una fallida, cierre); **no se debe afirmar que ambas pruebas constituyen una única ejecución E2E íntegra con la misma ruta** sin correlación documental.

## 2. Evidencias técnicas verificadas

| Frente | Resultado soportado | Fuente |
|---|---|---|
| QA CI | 163 pruebas aprobadas; 1 omitida; 0 fallidas; Android, Backend, Gateway y build web | [QA automation #6](QA_AUTOMATION_RUN_6_2026-11-20.md) |
| Operador web | Prueba de cinco pedidos; secuencia estimada 18.55→15.26 km y 32→25 min redondeados; aplicación mostró 19.43 % (porcentaje exacto pendiente de reconciliar) | [Piloto web 15/11](../EVIDENCIA_PILOTO_5_PEDIDOS_2026-11-15.md) |
| Android / conductor | US-012 iniciar, US-013 registrar paradas, US-014 completar: 5 DELIVERED, 1 FAILED, 0 pendientes | [QA final 21/11](US012_US013_US014_QA_FINAL_PASS_2026-11-21.md) |
| Firestore | Ruta QA COMPLETED v10; resumen 5/1; asignación liberada; ruta de otro conductor sin alteración en la verificación | [QA final 21/11](US012_US013_US014_QA_FINAL_PASS_2026-11-21.md) |
| Recuperación de historial | `own_route()` consulta `driver_last_routes/{uid}` cuando ya no existe asignación activa; permite mostrar ruta COMPLETED | `services/api/app/firestore_driver_assignment.py` |
| Android remoto | `AppContainer` conecta a tagged Gateway US-014 si Firebase está inicializado y `webClientId` existe; `DashboardViewModel.load()` llama `getAssignedRoutes` | `apps/driver-android/.../AppContainer.kt`, `DashboardViewModel.kt`, `ApiRouteRepository.kt` |
| Cloud Logging Gateway US-014 | GET `/api/v1/driver/me/route` HTTP 200 a las 22:46:18.486, 22:47:12.323 y 22:47:15.963 UTC, 21/11/2026 | Salida Cloud Shell presentada durante revisión 21/11 |
| Cloud Logging Backend US-014 | GET mismo endpoint HTTP 200 a las 22:46:18.555, 22:47:12.375 y 22:47:16.029 UTC, 21/11/2026 | Salida Cloud Shell presentada durante revisión 21/11 |

**Interpretación Cloud Logging:** coincidencia temporal compatible con tránsito Gateway→Backend (desfase de ~50–70 ms). No es correlación criptográfica ni evidencia de trace-id único. La petición exacta de Android no se atribuye de forma inequívoca solo con esos logs.

## 3. Relación con objetivos del caso UPN

- **OE1: reducir tiempo promedio de entrega 20 %.** *No demostrado con observación de campo.* Existe comparación de tiempos **estimados** de una previsualización.
- **OE2: disminuir distancia.** Evidencia de previsualización: 18.55 km frente a 15.26 km, diferencia estimada 3.29 km (~17.74 % de la cifra base mostrada). No es recorrido medido.
- **OE3: mejorar puntualidad.** *Pendiente de medición de ventanas horarias y eventos reales.*

El documento de alineación `docs/CAPSTONE_FIELD_REPORT_ALIGNMENT.md` describe 30 recorridos propuestos (15 manuales y 15 optimizados); no presentarlos como piloto ejecutado. El caso es **ficticio y académico**.

## 4. Entregables listos para mostrar en la sustentación

1. Diagrama de arquitectura y separación Gateway→API→Firestore en `docs/ARCHITECTURE_GCP.md` y `docs/diagrams`.
2. SDD, matriz de trazabilidad y decisiones de diseño en `docs/SmartRoute_AI_Charter_SDD_v1.md`, `docs/Matriz_Maestra_Capstone_SDD.md`, `docs/ADR.md`.
3. Evidencia reproducible de CI en `docs/evidence/QA_AUTOMATION_RUN_6_2026-11-20.md`.
4. Evidencia de optimización web en `docs/EVIDENCIA_PILOTO_5_PEDIDOS_2026-11-15.md`.
5. Evidencia de ejecución móvil, entregas, incidencias y persistencia en `docs/evidence/US012_US013_US014_QA_FINAL_PASS_2026-11-21.md`.
6. Esta ficha de avance técnico/académico y limitaciones.

Las **capturas originales del emulador y de la UI no constan como binarios versionados** según los informes. Adjuntarlas al documento de entrega si la rúbrica exige imágenes embebidas.

## 5. Guion de demostración (máximo 7 minutos de producto, si se exige el video de la rúbrica)

- **0:00–1:00** Contexto del problema, objetivo y solución; aclarar caso académico y datos controlados.
- **1:00–2:00** Arquitectura: React, Firebase, Gateway Cloud Run, FastAPI, OR-Tools/ORS, Firestore y Android.
- **2:00–3:30** Operador: creación/selección de pedidos y previsualización de ruta optimizada. Usar evidencia ya capturada si no se puede reproducir sin escrituras.
- **3:30–5:00** Android: vista de seis paradas, cinco entregadas, una fallida y estado COMPLETED. **No iniciar nuevas mutaciones sobre la ruta cerrada.**
- **5:00–6:00** CI 163 PASS + Firestore QA final + registros Gateway/API 200.
- **6:00–7:00** Limitaciones, KPIs estimados versus observados y pasos pendientes.

## 6. Pendientes priorizados

| Prioridad | Actividad | Criterio de cierre |
|---|---|---|
| P0 antes de presentar | Confirmar consigna/rúbrica exacta de la entrega del 22/11 | Índice y formato coinciden con lo pedido por docente |
| P0 | Incluir capturas, enlace CI, capturas de logs o export legible | Evidencias adjuntas, fechadas y con procedencia |
| P0 | Actualizar narrativa informe: Flutter/PostgreSQL del diseño original vs Android Kotlin/Firestore implementados | Diferencia documentada como cambio tecnológico y justificada |
| P0 | Verificar alcance P0 y criterios aceptados de la matriz académica | Porcentaje de requisitos P0 calculado sobre total congelado; sin confundir con ~65 % gerencial |
| P1 | Ejecutar demostración única Web→Optimización→Asignación→Android→Cierre | Misma ruta y mismo conjunto de pedidos, evidencias correlacionadas, previa autorización de escrituras de prueba |
| P1 | Controlar función QA de escritura Android | `ENABLE_QA_WRITE_TEST=false` antes de distribuir build general |
| P1 | Medir piloto comparable 15 A/15 B o versión aceptada por docente | Dataset, método, ventanas, tiempos observados, consentimiento si procede |
| P1 | Reconciliar porcentaje 19.43 % de pantalla con JSON exacto y cálculos | Misma base, unidades y cifras sin redondeo |
| P2 | Concluir matrices ética/SQA, resultados e informe final de rúbrica | Referencias y compromisos individuales completos |

## 7. Riesgos y control de cambios

- PR #56 sigue **sin merge**. Las revisiones US-014 están **etiquetadas al 0 % del tráfico principal**.
- No modificar IAM, rutas de tráfico Cloud Run, facturación o secrets sin autorización.
- Toda escritura de pruebas deberá ser explícitamente autorizada, aislada a Firestore `smartroute`; nunca a `(default)` o `gestioncitas`.
- OR-Tools garantiza la mejor solución encontrada bajo la configuración empleada, no óptimo global certificado.
- Tiempos/distancias del piloto web son estimaciones de matriz vial; no tiempos reales observados.

## 8. Veredicto para la entrega

**APTO PARA PRESENTAR COMO AVANCE FUNCIONAL DEL MVP**, condicionado a utilizar la rúbrica vigente y anexar evidencia visible. **NO APTO PARA DECLARAR PROYECTO FINAL TERMINADO NI META DE MEJORA DEL 20 % DEMOSTRADA.**
