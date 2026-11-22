# SmartRoute AI — Acta de validación E2E Operador → Android QA

**Fecha de prueba:** noche del 21/11/2026 en Lima / 22/11/2026 UTC.  
**Proyecto:** UPN Capstone SmartRoute AI.  
**Naturaleza:** caso académico, seis pedidos sintéticos, revisión QA controlada.  
**Fuente:** capturas y salidas Cloud Shell compartidas durante la sesión de validación, más código del repositorio. No se adjuntan aquí capturas binarias ni exportaciones completas de Cloud Logging; deben incorporarse al expediente de entrega cuando sea necesario.

## Identificación correlacionada de la prueba

| Campo | Dato verificado en la sesión |
| --- | --- |
| Ruta única E2E | `aec305db-6e2f-5923-8b9f-87fcd9b37755` |
| Conductor QA (Firebase UID) | `zMuwbYHLfST2QNdNkfosoCbUZ003` |
| Estado al asignar | `PLANNED`, 6 paradas |
| Estado al cerrar | `COMPLETED`, versión 10 informada por panel web |
| Resultados | 5 entregas exitosas; 1 fallida; 0 pendientes; 6/6 (100 %) |
| Distancia optimizada estimada | 16,8 km, frente a 20,96 km de referencia |
| Duración optimizada estimada | 31 min mostrados, frente a 36 min mostrados |
| Mejora mostrada por plataforma | 15,84 % (calculada con valores internos; no recalcular a partir de minutos redondeados) |
| Base | Firestore nombrada `smartroute`, proyecto `proyectopersonal-480420` |
| Preservación | La ruta de Manuel `681f7f60...` permaneció PLANNED en el panel final |

## Recorrido observado en UI

1. **Operador web**: ruta guardada/optimizada y asignada al UID QA; vista con secuencia persistida de 6 paradas y estado PLANNED.
2. **Android Kotlin/Compose**: inicio de sesión Google del conductor QA; misma ruta `aec305db...`, 6 paradas, 16,8 km y 31 min estimados, sin bandera de datos demo.
3. **Inicio US-012**: botón «Iniciar recorrido», diálogo de confirmación y acceso a la parada 1 con estado «En camino» y acciones activas.
4. **Ejecución US-013**: parada 1 marcada «Entregado» y controles bloqueados para evitar repetir el resultado; parada 2 «No entregado»; pantalla de resumen 2/6, 1 entregada, 1 fallida.
5. **Cierre US-014**: paradas 3–6 entregadas, resumen 6/6 (5 entregadas + 1 fallida, 0 pendientes), botón «Finalizar recorrido» y pantalla de inicio Android con estado «Completada».
6. **Lectura independiente**: panel del operador actualizado posteriormente presenta la **misma ruta** `aec305db...` en `COMPLETED`, versión 10, texto «recorrido finalizado», inicio registrado y las mismas métricas estimadas.

**Alcance de la afirmación:** prueba funcional E2E de interfaz y persistencia observable mediante lectura del operador. No se adjunta export independiente de documentos Firestore, log transaccional correlacionado por trace-id ni prueba de resistencia/concurrencia sobre esta ruta. Las capturas aportadas durante el chat son evidencia visual, pero **no** están almacenadas como archivos de imagen en este commit.

## Despliegue aislado y diagnóstico de incidente

| Elemento | Revisión/etiqueta | Notas |
| --- | --- | --- |
| Backend QA v2 | `smartroute-api-staging-00015-gih` · `qa-route-v2` | Guard de escritura por UID/ruta, sin tráfico principal |
| Gateway QA v2 (incidente) | `smartroute-gateway-staging-00015-xod` · `qa-gateway-v2` | GET `/api/v1/driver/me/route` devolvía 503 porque la URL nueva faltaba en `APPROVED_API_URLS` |
| Gateway QA v3 (resuelto) | `smartroute-gateway-staging-00016-pil` · `qa-gateway-v3` | Imagen Cloud Build `sha256:5102b36fe26477cf89bba666013ee4f2660b5fb12510390ebe40e5d0be8953ec`; lectura/acciones Android verificadas |
| IAM | `smartroute-gateway@proyectopersonal-480420.iam.gserviceaccount.com` | `roles/run.invoker` ya concedido al Backend: no fue necesario ampliar IAM |
| Tráfico principal Backend | `smartroute-api-staging-00010-juz` | 100 % según consulta durante la sesión antes del Gateway v3 |
| Tráfico principal Gateway | `smartroute-gateway-staging-00011-quj` | 100 % según consulta durante la sesión antes del Gateway v3 |

Se resolvió el fallo 503 incorporando la URL del Backend QA v2 a la **allowlist del Gateway**, commit `5323dee`. Las revisiones nuevas se desplegaron con `--no-traffic`; la salida del despliegue v3 confirma 0 %. Una relectura de toda la distribución del tráfico tras v3 sería evidencia adicional útil. El acceso `curl /health` directo al Backend privado devolvió 403 por ausencia de token: **no** debe interpretarse como falla de IAM ni justificar acceso público.

## Contratos/arquitectura validados

- Web OPERATOR: `POST /api/v1/orders`, `POST /api/v1/optimization/preview`, `POST /api/v1/optimized-routes`, `POST /api/v1/optimized-routes/{route_id}/assign-driver`.
- Android DRIVER: `GET /api/v1/driver/me/route`, `POST /api/v1/driver/me/route/start`, `POST /api/v1/driver/me/route/stops/{order_id}/deliver|fail` y `POST /api/v1/driver/me/route/complete`.
- Autenticación: token Firebase en Gateway; token IAM interno Cloud Run Gateway→Backend; autorización por propietario en Backend y guard QA por UID/ruta; Firestore nombrada `smartroute`.
- Tecnologías **implementadas**: React, FastAPI, Python OR-Tools, matriz vial openrouteservice, mapas OSM, Android Kotlin/Jetpack Compose, Firebase Authentication, Cloud Run y Firestore.
- **Fuera del flujo validado:** Gemini consultivo como función usable, GPS real, navegación giro a giro, optimización multivehículo, iOS, telemetría real, producción.

## Criterios de cierre y restricciones

- [x] Ruta única correlacionada desde operador a conductor y de vuelta al operador.
- [x] Inicio, cinco entregas, una incidencia y cierre visualizados en Android.
- [x] Estado final COMPLETED recuperado desde vista de operador.
- [x] Uso de UID/ruta QA con revisiones Backend y Gateway etiquetadas con 0 % del tráfico principal.
- [ ] Archivar capturas originales en `docs/evidence/assets/` y/o en entrega académica (actualmente no versionadas).
- [ ] Adjuntar export de trazas y lecturas directas Firestore para auditoría técnica independiente.
- [ ] Probar denegación por otros UID/rutas y aislamiento en CI, no únicamente permitir caso positivo.
- [ ] Verificar gates CI del commit de documentación y política de release Android.
- [ ] Ejecutar piloto con tiempos reales y evaluación de puntualidad; 15,84 % es **estimación**, inferior al objetivo hipotético 20 % y no mide ahorro operativo.

**Regla:** NO iniciar nuevas mutaciones contra esta ruta `COMPLETED`; NO incorporar el `ENABLE_QA_WRITE_TEST=true` local a una build de distribución, y NO acceder a Firestore `(default)` ni `gestioncitas`.
