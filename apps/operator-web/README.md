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
