# Checkpoint de ejecución — SmartRoute AI operador web y direcciones
**Fecha:** 2026-11-14 (America/Lima)  
**Repositorio:** https://github.com/JuliusCordova/SmartRoute_AI  
**Rama de trabajo:** `feat/operator-web-osm-routing-pilot`  
**PR de integración:** https://github.com/JuliusCordova/SmartRoute_AI/pull/53  
**Estado:** PAUSADO A PETICIÓN DEL USUARIO. Código registrado en GitHub; no se efectuó merge ni nuevo despliegue en este checkpoint.

## 1. Decisión de alcance
Prioridad **web-first** para Capstone UPN: primero panel OPERATOR para dar de alta pedidos, localizar direcciones sobre mapa OpenStreetMap, optimizar con matriz vial + OR-Tools y visualizar base vs. optimizada; después app Flutter/Android DRIVER. Una ruta optimizada **aún no se guarda ni publica** en este incremento. No presentar estimaciones como resultados observados del piloto.

## 2. Infraestructura verificada en proyecto compartido
Proyecto GCP `proyectopersonal-480420`, región `us-central1`.
- `smartroute-api-staging`: Cloud Run **privado**; acceso mediante proxy desde Cloud Shell `GET /health` = **HTTP 200**; `GET /api/v1/orders` sin Firebase Bearer = **HTTP 401**.
- `smartroute-gateway-staging`: `GET /health` = **HTTP 200**; `GET /api/v1/orders` anónimo = **HTTP 401**. Gateway público en infraestructura Cloud Run y protegido a nivel de Firebase en la aplicación. CORS anteriormente incluía `http://localhost:8080`; **no se ha verificado autorización del nuevo origen de Cloud Run**.
- `smartroute-web-staging`: desplegado desde `apps/operator-web`, revisión `smartroute-web-staging-00001-zbk`; URL `https://smartroute-web-staging-913797829604.us-central1.run.app`; `GET /health` = **HTTP 200** con `{"status":"ok","service":"smartroute-web"}`.
- El usuario vio frontend React y mapa OSM en el navegador y después **confirmó inicio de sesión exitoso con Google** una vez autorizado el dominio.
- Firebase app existente `smartroute-auth-test` (`projectId=proyectopersonal-480420`), el operador de prueba figura en Firestore nombrada `smartroute` con rol `OPERATOR` según checkpoints previos. **E2E pedidos desde la web actual no confirmado**.
- Aislamiento crítico: no tocar Firestore `(default)`, `gestioncitas`, servicios Atlas DataGob, LLMia ni aplicaciones ajenas. Todas las escrituras piloto exclusivamente en la base `smartroute`.

## 3. Código guardado en rama y PR #53
- `apps/operator-web/`: React, Firebase Google login, CRUD parcial de pedidos (POST/GET), mapa Leaflet + OSM, selección hasta 10 paradas y comparación visual. Dockerfile y servidor Node para Cloud Run.
- `services/api/app/route_preview.py`: lectura de matriz vial mediante openrouteservice y ejecución de OR-Tools en endpoint `POST /api/v1/optimization/preview`, salida con tiempo/km, huella y origen `estimated`; no escritura de ruta.
- `services/api/app/geocoding.py`: adaptador de búsqueda Geoapify, endpoint `GET /api/v1/geocoding/autocomplete?q=...`, hasta 5 alternativas con perímetro piloto de Lima y alertas por coincidencia aproximada.
- `apps/operator-web/src/main.jsx`: nueva interfaz autocomplete; el usuario escribe una dirección, selecciona una sugerencia, observa punto provisional y debe confirmar si la precisión es aproximada. No se exige ingresar manualmente coordenadas para el pedido.
- `services/gateway/app/main.py`: allowlist añadida para endpoints de preview y geocoding.
- Pruebas unitarias `services/api/tests/test_geocoding.py` y `test_route_preview.py`; CI extendida para compilar frontend y contenedor. ADR-13/14, SPEC y README actualizados.
- **Importante:** esta última mejora de autocompletado **solo está en la rama/PR**, no en la revisión web `00001-zbk` actualmente desplegada. El backend y gateway desplegados tampoco incluyen aún estos endpoints nuevos.

## 4. Evidencia de pruebas y bloqueo actual
- GitHub Actions workflow run `43559924157` correspondiente a commit anterior del PR (panel inicial): **api-tests PASS, firestore-emulator PASS, operator-web-build PASS**, deploy-staging SKIPPED. Estos resultados **no certifican los cambios posteriores de geocoding**.
- Cloud Shell ejecutó pruebas globales y fallaron en colección por `ModuleNotFoundError: No module named 'ortools'` (entorno Python global).
- Se intentó crear `services/api/.venv` e instalar `requirements.txt`; pip descargó dependencias, pero terminó con **`OSError: [Errno 28] No space left on device`**. No hay evidencia de instalación completa.
- El último paso recomendado, aún **NO ejecutado**, fue diagnóstico SOLO LECTURA:
  ```bash
  df -h "$HOME" /tmp && \
  du -sh ~/.cache/pip \
    ~/SmartRoute_AI/services/api/.venv \
    ~/SmartRoute_AI 2>/dev/null
  ```
- No borrar archivos ni cachés ajenos sin primero revisar espacio y seguridad del Cloud Shell compartido. Preferir GitHub Actions para pruebas reproducibles sin depender del almacenamiento local.

## 5. Para reanudar — secuencia verificable
1. Revisar estado del PR #53 y CI **más reciente**; verificar que los nuevos tests geocoding y build pasan y corregir si falla. Considerar estado de `.venv` local incompleto y disco lleno.
2. Configurar proveedor Geoapify y openrouteservice con cuentas/cuotas válidas; montar `GEOAPIFY_API_KEY` y `ORS_API_KEY` exclusivamente en backend privado mediante Secret Manager. Nunca enviarlas al frontend ni versionarlas en GitHub. Confirmar costos/políticas de proveedores y restricciones geográficas.
3. Planificar despliegues controlados de nuevos gateway y API sin cambiar IAM privado ni Firestore nombrada; alinear CORS para el origen exacto `https://smartroute-web-staging-913797829604.us-central1.run.app`, preservando orígenes requeridos. Probar 401/403, RBAC OPERATOR y límites.
4. Publicar nueva revisión de `smartroute-web-staging`. Verificar login Google, búsqueda de dirección, selección, alerta por ubicación aproximada, POST/GET pedido y persistencia en Firestore `smartroute`.
5. Probar matriz vial real y OR-Tools con 5–10 puntos ficticios, confirmar procedencia `estimated`, no ahorro observado; después implementar guardado/publicación ruta y finalmente Android.
6. Antes de merge a `main`, revisión de seguridad, pruebas CI y evitar activación accidental de despliegue automático sobre entorno compartido.

**No se han obtenido ni almacenado claves de Geoapify/openrouteservice, ni se ha demostrado E2E de geocodificación o optimización real.** No almacenar tokens Firebase, contraseñas ni claves privadas en commits o documentación.
