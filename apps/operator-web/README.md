## US-004 y tablero ejecutivo (implementación de rama)

Se incorpora un **Centro de Control Ejecutivo** con KPIs de pedidos y rutas, efectividad de entregas, mejora estimada ponderada, barras de estados y filtro de rutas. El panel carga las páginas de Firestore a través del Gateway con Firebase; si se alcanza el límite de páginas informa vista parcial. El módulo de pedidos incorpora filtros por estado y búsqueda combinada por dirección e ID, sin modificar datos.

El código y las pruebas puras están en `src/operations.js` y `tests/operations.test.js`; ejecutar `npm test` y `npm run build`. Los indicadores de ruta siguen siendo **estimated** y la puntualidad observada está pendiente. Hasta ejecutar E2E en la revisión web de QA, **US-004 y US-011 permanecen PARCIALES**.

Ver [`docs/US004_EXECUTIVE_COMMAND_CENTER_2026-11-22.md`](../../docs/US004_EXECUTIVE_COMMAND_CENTER_2026-11-22.md). Esta sección actualiza el estado de implementación de la rama; los párrafos históricos siguientes describen incrementos previos.

---
# SmartRoute AI — Operador web (React + Leaflet/OpenStreetMap)

**Estado:** código en rama, no desplegado todavía. React muestra datos persistidos en Firestore mediante el gateway; la previsualización usa una matriz vial real con OR-Tools, pero **no guarda ni publica** una ruta.

## Configuración

Servidor HTTP Node carga configuración pública desde variables Cloud Run y expone `/config.js` al navegador. Configuración Firebase Web es pública por diseño, no incluir contraseñas, claves privadas ni tokens IAM.

- `GOOGLE_CLOUD_PROJECT=proyectopersonal-480420`
- `GATEWAY_URL=https://smartroute-gateway-staging-913797829604.us-central1.run.app`
- `FIREBASE_API_KEY`, `FIREBASE_APP_ID`, `FIREBASE_AUTH_DOMAIN=proyectopersonal-480420.firebaseapp.com`, `FIREBASE_MESSAGING_SENDER_ID`: copiar de Firebase Console de la aplicación web correcta.
- `OSM_TILE_URL`: URL de teselas del proveedor elegido, con política de uso y atribución OSM. La opción OSMF por defecto es solo para piloto ligero, no una garantía de capacidad productiva.
- El gateway requiere `SMARTROUTE_ALLOWED_ORIGINS` incluyendo la **URL exacta** de Cloud Run web. No usar `*`.
- Firebase Authentication > dominios autorizados debe incluir **el dominio de Cloud Run exacto del frontend**, aprobado en el proyecto GCP compartido. Evitar alta de dominios de otros proyectos.

### Backend de optimización

El servicio FastAPI requiere `ORS_API_KEY` desde **Secret Manager**, configurado en la revisión privada de `smartroute-api-staging`, nunca en el frontend ni en GitHub. Debe tener permiso de Secret Manager exclusivamente para la cuenta de servicio runtime API. Endpoint vigente openrouteservice: `https://api.heigit.org/openrouteservice/v2/matrix/driving-car`.

### Despliegue (requiere revisión y aprobación antes de ejecutar)

1. Revisar cambios y CI del PR; no desplegar sobre Atlas DataGob u otros servicios.
2. Obtener las variables Firebase Web desde la consola y preparar Secret Manager para ORS.
3. Construir imagen de `apps/operator-web` en Artifact Registry y publicar **solo** `smartroute-web-staging`, región `us-central1`; registrar digest. El Dockerfile usa Node en modo no-root.
4. Configurar el dominio exacto en Firebase Auth, y en CORS del gateway sin quitar `http://localhost:8080` hasta validar el nuevo frontend.
5. Verificar web `/health`, 401 sin token en gateway, login Google y RBAC de OPERATOR. En Firebase no usar la cuenta administradora.
6. Verificar POST/GET pedidos persistidos exclusivamente en Firestore nombrada `smartroute`.
7. Configurar ORS y hacer POST `/api/v1/optimization/preview` con 1–10 pedidos de prueba; comprobar origen `estimated`, distancias, tiempos y `matrix_fingerprint`.
8. Guardado/publicación de la ruta queda para siguiente historia/PR. No etiquetar esta previsualización como piloto observado.

## Seguridad

Validación Firebase duplicada en gateway y API; API privada solo IAM; acceso Firestore con SDK servidor, no desde navegador. Máximo 10 destinos, coordenadas acotadas a Lima piloto. Las pruebas deben cubrir 401/403, matriz incompleta (422), proveedor no configurado (503), lista completa sin duplicados y que no se persistió ruta por la previsualización. Las cuotas de openrouteservice requieren restricción por operador y límites GCP de presupuesto/alertas antes de ampliar el piloto.

Ejecutar localmente con `npm install && npm run build`; para ejecutar la imagen se requieren las variables descritas. El botón de optimizar retorna un error controlado si falta `ORS_API_KEY`: **no sustituye con Haversine ni inventa cifras**.

## Autocompletado de direcciones (nueva capacidad)

El operador escribe 3–120 caracteres; el formulario consulta `GET /api/v1/geocoding/autocomplete?q=...` con Firebase Bearer a través del gateway. La API privada consulta Geoapify con filtro geográfico limitado al piloto de Lima y devuelve máximo 5 alternativas. La clave `GEOAPIFY_API_KEY` **solamente** pertenece al runtime privado de FastAPI, preferiblemente montada desde Secret Manager. No se muestra al navegador ni se almacena en Firestore.

En el panel, seleccionar una sugerencia determina sus coordenadas y dibuja un círculo verde temporal en el mapa; el operador no ingresa latitud/longitud. Si Geoapify no identifica número de inmueble, se advierte **ubicación aproximada** y se requiere marcar confirmación; sin selección no se puede guardar. Búsquedas sin resultados y errores del servicio dan avisos comprensibles. El área de búsqueda es un rectángulo piloto, no cobertura real de una operación comercial. Todos los pedidos demo deben ser **ficticios**, no domicilios personales.

**Pendiente de activación:** crear clave Geoapify con cuotas y restricciones; guardarla en Secret Manager de SmartRoute y dar acceso solo a runtime API. Actualizar contenedores de gateway y backend en staging, manteniendo backend IAM privado, y configurar CORS exacto del dominio web. El frontend ya desplegado **no incorpora esta mejora** hasta construir una revisión nueva. No afirmar E2E validada hasta prueba real con cuenta OPERATOR.

El proveedor OSMF público de Nominatim prohíbe su uso como autocomplete; no se utiliza. Fuentes: https://apidocs.geoapify.com/docs/geocoding/address-autocomplete/ y https://operations.osmfoundation.org/policies/nominatim/.
