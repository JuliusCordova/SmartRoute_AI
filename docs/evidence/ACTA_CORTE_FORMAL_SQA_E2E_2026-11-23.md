# SmartRoute AI — Acta de corte formal de calidad y pruebas E2E
**Corte técnico:** 23 de noviembre de 2026 (America/Lima)  
**Proyecto:** Capstone UPN — SmartRoute AI  
**Caso:** `TC-E2E-QA-20261123-02` · **Entorno:** QA etiquetado de GCP + emulador Android Pixel 9 Pro XL  
**Alcance:** datos sintéticos; **no** corresponde a entregas físicas, medición de distancia recorrida ni certificación de producción.

## 1. Dictamen ejecutivo y alcance

**APROBADO — flujo operativo funcional QA de esta ruta**, condicionado a mantener las limitaciones y acciones SQA abiertas en los apartados siguientes. Se demostró el ciclo **operador web → optimización y persistencia → asignación → Android DRIVER → inicio → ubicación GPS simulada consentida y persistida → resultado de 5 entregas → cierre → liberación del conductor y limpieza GPS**. No se ha validado despliegue productivo, cobertura completa de pruebas negativas/RBAC, accesibilidad, rendimiento, seguridad de producción, piloto real comparable ni el objetivo del 20 % de ahorro.

**Relación con pruebas previas:** se trata de un **segundo recorrido distinto** del acta [E2E 21–22/11](E2E_OPERADOR_ANDROID_QA_2026-11-22.md) de seis paradas (`aec305db-...`). No mezclar sus pedidos, versiones, métricas ni evidencias.

## 2. Identificadores inmutables del escenario

| Elemento | Valor |
| --- | --- |
| Proyecto y región GCP | `proyectopersonal-480420`; `us-central1` |
| Base Firestore | **`smartroute`**, no `(default)` ni `gestioncitas` |
| Ruta QA | `fb413b71-c963-570f-be61-500e9eadfb7b` |
| Firebase UID del conductor QA | `zMuwbYHLfST2QNdNkfosoCbUZ003` |
| Centro origen | `SEDE-SUR San Isidro` (coordenadas aproximadas `-12.09737,-77.02128`) |
| Paradas | 5, en orden optimizado persistido |
| Distancia/tiempo estimados (Android) | **41,7 km / 61 min**, **NO** valores medidos |
| Comparación de optimización presentada por operador | 48,43 km / 71 min de referencia → 41,68 km / 61 min optimizados; **14,59 % de mejora estimada** reportada por plataforma, no recalcular sobre cifras redondeadas |
| Conductor | misma identidad para lectura, inicio, entrega, GPS y cierre |
| Gateway etiquetado | `qa-90681ae`; revisión inicialmente verificada `00018-yek`, sin tráfico principal |
| API etiquetada | `qa-bca4df3` → revisión `smartroute-api-staging-00017-way`, con 0 % de tráfico |
| Guard Backend | `SMARTROUTE_QA_WRITE_GUARD=true`, UID/ruta exactos, `FIRESTORE_DATABASE_ID=smartroute` |
| Tráfico API principal comprobado al habilitar el caso | `smartroute-api-staging-00010-juz` 100 %; QA `00017-way` 0 %. **No extrapolar esta observación a cualquier instante posterior.** |
| Código Android de simplificación QA | [PR #73](https://github.com/JuliusCordova/SmartRoute_AI/pull/73), merge `c309a59`; las escrituras QA de *release* siguen bloqueadas |

## 3. Secuencia ejecutada y evidencias

| ID | Criterio / actividad | Resultado respaldado | Evidencia de la sesión |
| --- | --- | --- | --- |
| E23-01 | Login del conductor y lectura de ruta propia | **PASS funcional**: tarjeta y detalle Android de ruta PLANNED y 5 paradas | Capturas Android, pantalla «Mis rutas» y detalle |
| E23-02 | Secuencia y métricas de optimización | **PASS QA visual**: San Isidro → Arequipa → Guardia Civil → Separadora Industrial → Emancipación → Morro Solar; OSM con línea de secuencia, no geometría vial | Capturas detalle Android/operador |
| E23-03 | Controles para iniciar ruta | **PASS**: después de corregir restricciones duplicadas, aparece botón y confirmación explícita | Capturas «Iniciar recorrido»; PR #70–#73 |
| E23-04 | Transición PLANNED→ACTIVE | **PASS funcional**: Android cambia acciones y presenta autorización GPS. La persistencia no se consultó como chequeo independiente justo tras inicio, pero el Backend aceptó luego GPS y cierre condicionado a ACTIVE | Capturas antes/después |
| E23-05 | GPS con consentimiento durante ACTIVE | **PASS QA emulador**: permiso «While using the app», precisión reportada 5 m, última transmisión aceptada por Android | Capturas permiso y pantalla «Último envío» |
| E23-06 | Persistencia de última posición | **PASS Firestore REST HTTP 200**: `driver_last_locations/{routeId}`; lat `-12.097368333333334`, lon `-77.02128`, `accuracy_m=5`, `captured_at=2026-11-23T19:20:35.010Z`, `stored_at=2026-11-23T19:20:39.014052Z`. **Ubicación simulada**, no trayecto real | Salida Cloud Shell copiada por el ejecutor |
| E23-07 | Entrega exitosa primera parada | **PASS Android + REST Firestore**: pedido `dc570c6d-4b92-4d44-a0c7-843c05c29bbd`, `DELIVERED`, HTTP 200, bloqueo visual de doble entrega, progreso 1/5 | Capturas Android y Cloud Shell «Estado: DELIVERED / PASS» |
| E23-08 | Entrega fallida segunda parada | **PASS Android + REST Firestore**: motivo obligatorio (máximo 250 caracteres en UI), pedido `5005b416-e649-48fd-8c7d-60b9167783e7` `FAILED`, HTTP 200, progreso 2/5 | Capturas formulario, resumen y Cloud Shell «Estado: FAILED / PASS» |
| E23-09 | Tercera, cuarta y quinta paradas | **PASS funcional Android**: tres DELIVERED, progresos 3/5, 4/5 y 5/5; **no** hay aquí GET REST individual para estas tres órdenes | Capturas Android sucesivas |
| E23-10 | Cierre US-IMP-014 | **PASS**: diálogo de confirmación; Android muestra «Recorrido completado: 4 entregadas y 1 fallidas», 5/5, 0 pendientes | Capturas de confirmación y estado final |
| E23-11 | Persistencia de cierre y recuperación | **PASS REST Firestore**: `routes/{routeId}.status=COMPLETED` HTTP 200; `driver_last_routes/{uid}.route_id={routeId}` HTTP 200 | Salida Cloud Shell (cinco comprobaciones PASS) |
| E23-12 | Disponibilidad del conductor y liberación | **PASS REST Firestore**: `drivers/{uid}.available=true` HTTP 200; `driver_assignments/{uid}` HTTP 404 | Misma consulta de cierre |
| E23-13 | Eliminación de ubicación tras cierre | **PASS REST Firestore**: `driver_last_locations/{routeId}` HTTP 404 tras cierre; no mantener tracking indefinido | Misma consulta de cierre |
| E23-14 | Regresión general y seguridad de distribución | **PARCIAL**: workflows CI y QA del PR #73 en verde; no se adjuntan aquí ejecuciones de pruebas negativas en ambiente desplegado ni pen-test. | [PR #73](https://github.com/JuliusCordova/SmartRoute_AI/pull/73), GitHub Actions |

**Distinción:** `4 DELIVERED + 1 FAILED = 5 resueltas` equivale a **100 % de resolución de paradas**; la **tasa de entrega exitosa es 80 %**, no 100 %. Los estados son resultados de una simulación académica.

## 4. Incidentes, causa y remediación

| ID | Incidente | Remediación y aprendizaje | Estado al corte |
| --- | --- | --- | --- |
| INC-23-01 | Botón de inicio oculto; autorización duplicada Android (`QA_WRITE_TEST_ENABLED`, UID, ruta) y desajuste temporal del guard QA Backend | Backend QA 0 % tráfico con ruta correcta; PR #70–#73; reducción de restricción cliente debug a UID, preservando control de ruta/rol en servidor; QA del PR #73 exitoso | **Resuelto funcionalmente** |
| INC-23-02 | `BuildConfig` generado con `false`, builds repetidas, dudas sobre APK realmente instalada y hashes distintos en comprobación previa | Revisión del build e instalación; simplificación debug en PR #73, build normal y ADB; apertura posterior del botón y ejecución completada | **Resuelto funcionalmente**; causa exacta de diferencia SHA anterior **no demostrada** |
| INC-23-03 | Fallos de compilación CI por `AppConfig` importado dos veces | Deduplicación con logs del job Android y gate doble CI+QA antes del merge | **Resuelto** |
| INC-23-04 | Primer GPS: «El servidor no confirmó la operación» | Posición del emulador inicialmente fuera del ámbito de Lima, fijada en `-12.09737,-77.02128`; segundo envío aceptado y REST 200 | **Resuelto en laboratorio**; causa del primer error plausible, no confirmada por HTTP exacto |
| INC-23-05 | La app Google del emulador no responde | Se cerró aplicación Google; SmartRoute Driver persistió y continuó normalmente | **No bloqueante** |
| INC-23-06 | Línea vertical superpuesta sobre mapa/detalle de pedido | Captura visual, causa aún no aislada | **Defecto UI abierto** |
| INC-23-07 | Nombre de origen muestra «Depósito» en lugar de «SEDE-SUR San Isidro» | `DriverRouteParser` usa nombre genérico; falta proyección del nombre de sede | **Deuda UI/contrato** |
| INC-23-08 | Mapa conecta paradas en línea recta, no calles | El mapa lo indica expresamente; no anunciar navegación giro a giro ni distancia real trazada | **Limitación de alcance** |

Ver historial detallado, incluyendo Git/PowerShell/AVD, en [Lecciones aprendidas](LECCIONES_APRENDIDAS_ANDROID_QA_2026-11-23.md).

## 5. Aseguramiento de calidad y controles

- **Identidad y autorización:** Google/Firebase con UID QA, Gateway autenticado, Backend rol DRIVER/propiedad y guard UID + ruta. No se ejecutó prueba negativa desplegada contra otro conductor en este escenario.
- **Control de versión:** cambios de Android mediante PR #70, #71, #72 y #73; CI y QA Automation verdes en #73. El presente corte solo documenta; no actualiza aplicación ni GCP.
- **Segregación:** Firestore nominada `smartroute`; API QA etiquetada con 0 % del tráfico en comprobación previa. No hay evidencia de tráfico alterado por las pruebas de usuario.
- **Privacidad:** GPS capturado solo con permiso; documento de última ubicación eliminado al finalizar la ruta, verificado por HTTP 404. **Atención:** en el documento inicial figura `data_origin=observed` por implementación; la fuente de la coordenada fue un **emulador**, por lo que en el reporte académico debe indicarse `SIMULATED_QA`. No inferir movilidad observada.
- **Reproducibilidad:** commits/PR, ruta y UID, comandos REST y timestamps permiten auditar el recorrido; las capturas están en la conversación, **no se declaran versionadas como archivos de imagen en GitHub**.
- **Alcance del indicador:** intervalo `captured_at → stored_at` ~4.004 s; **no** es latencia HTTP medida, ni velocidad de viaje ni SLA.

## 6. Matriz breve de criterios y gates pendientes

| Frente | Estado al corte | Gate necesario para uso fuera de QA |
| --- | --- | --- |
| US-IMP-012 inicio | PASS funcional QA | Negativas de rol/usuario, reintentos/concurrencia, observabilidad por trace-id |
| US-IMP-013 resultados | PASS QA, 2 órdenes verificadas directo en REST | Verificar 3 órdenes restantes en REST/export; errores/reintentos/idempotencia |
| US-IMP-014 cierre | **PASS E2E por REST 5/5** | Regresión de seguridad, recuperación ante error y ambiente productivo separado |
| US-V1-008 GPS | **PASS funcional QA emulador** | Dispositivo físico, variación de ruta, consentimiento/revocación, payload/estado, distinción datos simulados y reales |
| Optimización | PASS funcional estimado | Muestras comparables, medidas realmente observadas, prueba experimental |
| SQA, seguridad y ética | Controles implementados, evidencias positivas de QA | Auditoría negativa de RBAC, privacidad, accesibilidad, impacto social/ambiental/legal y consentimiento |
| Evidencias formales | Acta y salidas en conversación; repositorio con texto | Adjuntar capturas saneadas, checksums, export de logs y informe final |
| Producción | **NO APROBADO** | Hardening, SRE/runbook, pruebas de carga y aceptación académica/usuario |

## 7. Control de cambios / congelamiento

1. **Congelar este caso:** no volver a modificar ni reabrir la ruta `fb413b71-...` (COMPLETED), ni usarla para nuevas mutaciones.
2. No cambiar roles, IAM, secrets, tráfico principal de Cloud Run ni las bases `(default)` y `gestioncitas`.
3. Versionar este corte por PR y exigir CI/QA verde antes de fusionarlo.
4. **No atribuir:** aprobación de producción, ahorro real del 20 %, confirmación de entrega física, pruebas A/B ejecutadas ni cobertura total de rúbrica UPN.

**Dictamen profesional:** **GO para demostración y documentación del MVP académico en QA**, **NO-GO para producción o afirmaciones de impacto operativo real**.
