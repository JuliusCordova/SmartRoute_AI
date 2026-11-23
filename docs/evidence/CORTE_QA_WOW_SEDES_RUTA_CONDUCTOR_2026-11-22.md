# SmartRoute AI — Corte de evidencias QA: Dashboard WOW, filtros, sedes y ruta asignada

**Fecha del corte:** 22/11/2026, hora de Lima (capturas finales cercanas al cambio de fecha UTC).
**Ámbito:** proyecto GCP `proyectopersonal-480420`, región `us-central1`, Firestore **nombrada** `smartroute`; escenario sintético de Capstone UPN.
**Tipo:** evidencias funcionales aportadas por el operador mediante capturas de la aplicación, más salidas verificadas de Cloud Shell. **No es certificación de producción ni medición operativa real.**

## 1. Despliegue reproducible y aislamiento QA

| Servicio | Imagen / referencia | Revisión QA | Tráfico principal |
| --- | --- | --- | --- |
| API privada | `smartroute-api@sha256:634f6ad1eea4b22ba898cbd02fbf70b49f64296b61a6311630e47a93d344661b` | `smartroute-api-staging-00016-siq`, etiqueta `qa-bca4df3` | 0 % |
| Gateway | `smartroute-gateway@sha256:9191b2077adac203bd665955d501baf7c1298752673605af3b8199ce96a1308a` | `smartroute-gateway-staging-00018-yek`, etiqueta `qa-90681ae` | 0 % |
| Web operador | `smartroute-operator-web@sha256:02fdc6e3446c37f2e5bda3bbb63ceb1acbaff6f893b478d64638fd44873a8639` | `smartroute-web-staging-00010-jef`, etiqueta `qa-wow-bca4df3` | 0 % |

- Fuente del API/Web: código `bca4df3`; el Gateway incluyó corrección de allowlist del PR #68, merge `90681ae`.
- Compilaciones Cloud Build verificadas: API `8a62b3e4-a63d-4335-81f4-2bf71601f26a`, Gateway final `c1b6065a-9bcd-4178-abf8-12ff6b1fc554`, web `f016dccd-ab75-4704-8d07-b8778342456c`; todas `SUCCESS`.
- Tráfico API principal `00010-juz` = 100 %, Gateway principal `00011-quj` = 100 % al verificarlos; revisión QA por etiqueta sin participación en tráfico normal. No consta promoción a 100 % ni cambio de IAM.
- `GET /health` del Gateway QA devolvió HTTP 200. Preflight OPTIONS desde dominio QA web hacia `/api/v1/orders` devolvió HTTP 204 con `access-control-allow-origin` exacto.
- El inicio de sesión QA inicialmente falló con `auth/unauthorized-domain`; se autorizó el dominio exacto en Firebase Authentication y posteriormente se comprobó inicio exitoso y lectura del dashboard.
- Nota de seguridad: la API sigue bajo IAM; conservar guardas de escritura QA y no alterar bases `(default)` ni `gestioncitas`. Estas capturas no demuestran una revisión exhaustiva de RBAC ni controles negativos.

## 2. Evidencias de aceptación observadas

| ID evidencia | Función | Observación específica | Resultado de este corte |
| --- | --- | --- | --- |
| N01 | Inicio de sesión y dashboard ejecutivo | Sesión autenticada; 18 pedidos, 3 rutas, efectividad 83,3 %, mejora mostrada 15,0 % estimada | PASS lectura/UI |
| N02 | Filtro ejecutivo de rutas | Selección `Finalizadas`: 2 rutas, mejora mostrada 13,6 % estimada; pedidos permanecen en 18 | PASS filtro visual |
| N03 | US-V1-004 pedidos por estado | `No entregados`: 2 de 18, ambos `FAILED` | PASS |
| N04 | US-V1-004 pedidos por estado | `Entregados`: 10 de 18, filas `DELIVERED` | PASS |
| N05 | US-V1-004 pedidos por estado | `Todos`: 18 de 18 registros | PASS |
| N06 | US-017 registro catálogo | Usuario reporta 3 sedes creadas; listado de 3 sedes recuperadas en Firestore; geocodificación visible | PASS funcional en muestra |
| N07 | US-017 búsqueda | Cadena `norte` devuelve `SEDE-NORTE Los Olivos` código 01 | PASS |
| N08 | US-017 edición | Formulario de código 01 precargado y mensaje `Sede 01 actualizada` | PASS acción visual |
| N09 | US-017 desactivación | Confirmación de desactivación; `SEDE-NORTE` se muestra `INACTIVA` y botones bloqueados | PASS |
| N10 | US-017 selección | `SEDE-SUR San Isidro` código 02 seleccionada; dirección y coordenadas aproximadas con confirmación del origen | PASS |
| N11 | Optimización con nueva sede | 5 pedidos `PENDING` seleccionados de un total de 23; mapa OSM con recorrido estimado y panel comparativo | PASS ejecución visual |
| N12 | Persistencia | Ruta `fb413b71-c963-570f-be61-500e9eadfb7b` recuperada como `PLANNED`, 5 entregas, 41,68 km | PASS recuperación |
| N13 | Referencia persistente a sede | Detalle dice `Centro de distribución: SEDE-SUR San Isidro · 38891a81` | PASS vínculo visible |
| N14 | Asignación a conductor | Conductor QA SmartRoute (identificador visible abreviado `zMuwbYHL`); ruta `fb413b71` cambia de `Sin conductor` a `Asignada`, manteniendo `PLANNED` | PASS funcional visual |

**Rutas en la captura posterior al guardado:** 4 recuperadas; filtro `Planificadas` muestra 2 (ruta `681f7f60` ya asignada y la ruta nueva `fb413b71`). No cambiar la ruta QA histórica ya completada `aec305db-6e2f-5923-8b9f-87fcd9b37755`.

## 3. Ensayo de optimización OR-Tools + openrouteservice

- Centro seleccionado y persistido: **SEDE-SUR San Isidro**, código `02`, coordenadas aproximadas `-12.09737, -77.02128`, origen confirmado manualmente.
- Cinco pedidos sintéticos nuevos con estado inicial `PENDING`; la ruta fue guardada y después asignada a conductor QA.
- Ruta persistida: **`fb413b71-c963-570f-be61-500e9eadfb7b`**.
- Baseline mostrado: **71 min / 48,43 km**.
- Ruta optimizada guardada: **61 min / 41,68 km**.
- Mejora estimada informada por la aplicación: **14,59 %**, origen `openrouteservice`; porcentajes y tiempos redondeados no necesariamente coinciden en una resta manual simple.
- Secuencia persistida: centro de distribución → Av. Arequipa 3067 (San Isidro) → Av. Guardia Civil 567 (San Isidro) → Av. Separadora Industrial 789 (San Luis) → Av. Emancipación (Lima) → Morro Solar 6789 (Chorrillos) → retorno al centro.
- El mapa cargó teselas OpenStreetMap y el trazado vial estimado; un pantallazo temprano mostró cuadrícula parcial, posteriormente resuelta al cargar las teselas.
- **No** se ha medido tiempo real de reparto, recorrido GPS, puntualidad, experimento A/B, ni se alcanzó mediante evidencia observada el objetivo académico de mejora >=20 %.

## 4. Estado de aceptación conservador

- **US-V1-004**: filtro por estado de pedidos aceptado funcionalmente en QA para `Todos`, `FAILED`, `DELIVERED`. Sin pruebas documentadas de búsqueda combinada ID/dirección o casos límite.
- **Dashboard ejecutivo / US-V1-011**: indicadores y filtro de rutas funcionales, **parcial** en el criterio integral de puntualidad y tiempos observados.
- **US-017**: CRUD (crear/listar/buscar/editar/desactivar), selección de sede activa, optimización y referencia guardada verificadas en QA. Sin suite de concurrencia, intentos negativos de roles ni reactivación demostrada.
- **US-V1-008 (GPS)**: **pendiente E2E**; no se evidencia lectura GPS del teléfono ni publicación de muestras desde Android durante `ACTIVE`.
- **US-V1-015 (piloto comparable)**: pendiente, no extrapolar los resultados sintéticos.
- **Android ruta nueva**: aún **no** se ha mostrado la nueva ruta en Android con la identidad del conductor QA. Asignada no significa iniciada ni completada.

## 5. Pendientes al reanudar

1. Abrir Android Studio/emulador con la cuenta del conductor QA y verificar que reciba exactamente `fb413b71` con cinco paradas, sin iniciar ruta.
2. Validar inicio de ruta `ACTIVE`, consentimiento GPS, geolocalización observada y actualización/lectura en operador; registrar timestamps y permisos, sin simular métricas reales.
3. Probar resultados de entrega y cierre de esta **nueva** ruta solo si el entorno y el guard de escrituras QA permiten la prueba deliberadamente.
4. Documentar casos negativos de RBAC, filtros de búsqueda, idempotencia/concurrencia y restricciones de sedes inactivas.
5. Ajustar texto de retorno `Depósito` a `Centro de distribución` en secuencia persistida; es una inconsistencia de nomenclatura visual.
6. Archivar los archivos originales de las capturas con manejo de datos de identidad antes de anexarlos al informe académico.

## 6. Origen y límites del material

Las capturas N01–N14 fueron entregadas en la conversación durante la ejecución del piloto. **Este commit registra sus observaciones, pero no incorpora archivos PNG binarios**. No se inventan SHA-256 de capturas ni se afirma que estén disponibles desde GitHub. El informe final debe vincular/anexar las imágenes originales autorizadas. Los valores de 14,59 %, 15,0 % y 13,6 % son estimaciones de escenarios/filtros distintos, no KPIs observados de producción.
