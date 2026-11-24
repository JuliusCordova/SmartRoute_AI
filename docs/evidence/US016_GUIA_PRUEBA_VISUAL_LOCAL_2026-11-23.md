# US-016 — Procedimiento reproducible de prueba visual local (Windows + Cloud Shell)

**Fecha:** 23/11/2026. **Estado:** escenarios A (`IN_TRANSIT`) y B (`FAILED`) verificados visualmente con simulador HTTP en Windows/localhost. **No es una prueba E2E de GCP** ni demuestra seguridad de tokens productivos.

## Objetivo
Abrir `apps/customer-tracking` en Chrome de Windows usando un servidor HTTP **sintético** en Cloud Shell y un túnel SSH local, evitando el bloqueo CORS del proxy de vista previa web de Cloud Shell. No modificar ni desplegar Cloud Run, Firebase, Firestore, ni `main`.

## Requisitos
- Cloud Shell con checkout de `~/SmartRoute_AI` que contenga `apps/customer-tracking`.
- Windows PowerShell con Google Cloud CLI (`gcloud --version` comprobado: SDK 575.0.0).
- Cuenta Google autorizada para Cloud Shell y PuTTY/OpenSSH configurado por `gcloud`.
- Dos terminales independientes (una para servidor y otra para túnel). Mantener ambos procesos activos.
- Los tokens sintéticos de esta guía son repetitivos y **NO** son seguros: no usarlos fuera de esta demo.

## 1. Servidor HTTP sintético en Cloud Shell (terminal A)
Desde Cloud Shell (sin imprimir ni copiar el prompt de la consola), ejecutar:

```bash
cd ~/SmartRoute_AI/apps/customer-tracking
python - <<'PY'
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json

ORDERS = {
    "A" * 43: {"order_reference": "SR-DEMO-A", "status": "IN_TRANSIT", "eta_minutes": None},
    "B" * 43: {"order_reference": "SR-DEMO-B", "status": "FAILED", "eta_minutes": None},
}

class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/api/v1/public/tracking":
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 1024:
                self.send_error(400)
                return
            payload = json.loads(self.rfile.read(size))
            token = payload.get("token")
            order = ORDERS.get(token) if isinstance(token, str) else None
        except (ValueError, TypeError, AttributeError):
            order = None
        body = json.dumps(order or {"detail": "Not found"}).encode("utf-8")
        self.send_response(200 if order else 404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

print("Simulador US-016 activo en puerto 8081", flush=True)
ThreadingHTTPServer(("127.0.0.1", 8081), Handler).serve_forever()
PY
```

Esperado: `Simulador US-016 activo en puerto 8081`. **No cerrar esta terminal.** Si la sesión terminó, reiniciarla; si el puerto está ocupado, detener únicamente el servidor anterior que usa 8081. El servidor estándar `python -m http.server` sirve archivos, pero **no implementa POST** y no sustituye al simulador de arriba.

Comprobación opcional en otra terminal de Cloud Shell:
```bash
curl -i http://127.0.0.1:8081/api/v1/public/tracking \
  -H 'Content-Type: application/json' \
  -d "{\"token\":\"$(printf 'A%.0s' {1..43})\"}"
```
Esperado: `HTTP/1.0 200 OK` con JSON `SR-DEMO-A` / `IN_TRANSIT` / `eta_minutes:null`.

## 2. Túnel desde Windows PowerShell (terminal B)
```powershell
gcloud --version
gcloud cloud-shell ssh --authorize-session --ssh-flag="-L" --ssh-flag="127.0.0.1:8081:127.0.0.1:8081"
```

La **separación en dos `--ssh-flag`** es crítica en Windows/PuTTY. Un único `--ssh-flag="-L 127.0.0.1:8081:127.0.0.1:8081"` produjo `PuTTY Command Line Error: unknown option`. Antes de ejecutar el túnel se verificó `gcloud cloud-shell ssh --authorize-session`, que abrió una sesión PuTTY satisfactoriamente.

Esperado: terminal PuTTY conectada a Cloud Shell y túnel abierto. Mantenerla activa. El proyecto GCP mostrado en la bienvenida de Cloud Shell no altera esta prueba local.

## 3. Abrir casos en Chrome **desde Windows localhost**, NO desde la URL `.cloudshell.dev`
**Pedido A (en camino):**
```text
http://127.0.0.1:8081/#/t/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
```

**Pedido B (entrega fallida):**
```text
http://127.0.0.1:8081/#/t/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
```

Resultados esperados:
- A: `PEDIDO SR-DEMO-A`, `Pedido en camino`, sin ETA calculada ni GPS/recorrido.
- B: `PEDIDO SR-DEMO-B`, `Entrega no completada`, sin datos del pedido A; **PASS visual en Chrome Windows**.
- Sin token: `Enlace inválido`.
- Token con formato correcto pero no registrado: `Seguimiento no disponible` (respuesta HTTP 404 del simulador).
- Comprobar también vista móvil en DevTools (320 × 650 px), lectura, ausencia de desbordamiento y datos privados.

No abrir URLs que contengan tokens reales de clientes en conversaciones, capturas o herramientas externas.

## 4. Diagnóstico reproducible del bloqueo anterior
Al abrir el seguimiento por la URL de vista previa `https://8081-...cloudshell.dev/#/t/...` el navegador mostró `No se pudo consultar`. DevTools Console confirmó redirección de la solicitud a `https://ssh.cloud.google.com/cloudshell/jwt?redirect_uri=...` seguida de bloqueo CORS (falta `Access-Control-Allow-Origin`) y 302. El simulador **no recibió el POST** desde la vista previa. Por tanto, la prueba visual válida se hizo a través del túnel local. Esto **no justifica relajar CORS del gateway real**.

## 5. Evidencia obtenida y límites
- **PASS:** captura de Chrome Windows en `127.0.0.1:8081` con pedido `SR-DEMO-A` mostrado como `Pedido en camino`, texto de ETA no disponible y aviso de privacidad. Captura compartida en la conversación del 23/11/2026; **la imagen no está subida como binario a este repositorio**.
- **PASS previo:** `curl` con pedido sintético A => 200 + JSON esperado.
- **PASS:** captura B en Chrome Windows en `127.0.0.1:8081`, con `SR-DEMO-B`, mensaje `Entrega no completada`, sin ETA ni GPS ni datos del pedido A. Captura compartida en conversación del 23/11/2026; **no subida como binario a GitHub**.
- **PASS:** token de formato válido pero desconocido (`C` repetido 43 veces) mostró «Seguimiento no disponible» y mensaje para solicitar nuevo enlace; sin datos de pedido. Captura aportada en conversación del 23/11/2026, aún no subida como imagen binaria al repositorio.
- **PASS:** vista móvil Chrome DevTools 320 × 650 px con pedido A válido (`SR-DEMO-A`, `Pedido en camino`), contenido legible, sin desbordamiento horizontal visible, ETA no disponible, sin GPS/recorrido ni errores visibles en consola. Captura compartida en conversación del 23/11/2026; **no subida como imagen binaria al repositorio**.
- **QA visual local cerrada para escenarios A, B, token desconocido y vista móvil A.** Esta conclusión se limita al frontend + simulador sintético por túnel SSH.
- **PENDIENTE:** comparación final con prototipo y E2E con API/gateway reales en entorno aislado; controles de seguridad perimetral y despliegue.
- **No confundir:** el simulador acepta claves ficticias `A*43` y `B*43`, por lo que no valida generación criptográfica, expiración o control de acceso real. Eso requiere las pruebas del backend/emulador y seguridad perimetral.
- Mantener PR #81 (frontend), #82 (backend) y #83 (evidencia) abiertos y sin activar el seguimiento público hasta QA integral.

## Cierre de sesión
Para detener el simulador: `Ctrl+C` en la terminal A. Para cerrar el túnel: `exit` en PuTTY. No detener otros servicios Cloud Shell ni eliminar archivos generados.

## 6. Prueba integrada HTTP simulada: gateway → backend (23/11/2026)

**Resultado de ejecución manual en Cloud Shell:**
```text
PASS: Pedido A
PASS: Pedido B
PASS: Token desconocido
PASS: Revocación independiente
PASS: Operador protegido
RESULTADO: INTEGRACION A/B APROBADA
```

Se cargó la aplicación FastAPI de la API con repositorio sintético en memoria (`test_public_tracking.setup()`), y la aplicación FastAPI del gateway en el mismo intérprete. El método `httpx.AsyncClient.request` del gateway fue sustituido por un adaptador que llama `TestClient(api_app)`. La obtención de ID token IAM se sustituyó por el valor ficticio `iam`. El feature gate público fue activado **solo dentro de `patch.dict(os.environ,...)` de ese proceso**, sin alterar configuraciones GCP.

- Token A → HTTP 200, referencia A y campos públicos limitados.
- Token B → HTTP 200, referencia B y campos públicos limitados.
- Token sintético desconocido → HTTP 404.
- Revocar A → HTTP 404 para A; B siguió respondiendo HTTP 200.
- `GET /api/v1/orders` sin Firebase → HTTP 401.

**Alcance preciso:** comprobación de contrato entre las dos aplicaciones FastAPI a través de transporte sustituido; no es una llamada real a Cloud Run ni prueba de Firestore, IAM o infraestructura real. No se alteró `main`, no se hizo despliegue. La evidencia de ejecución es la salida de terminal compartida por el usuario en la conversación; no se ha almacenado una captura binaria en GitHub.

**Pendiente para QA integral:** E2E aislado con transporte real, control de tasa perimetral, verificación de logs sin secretos, CORS/referrer/no-store, compatibilidad UX con prototipo y entrega segura de enlaces. Las pruebas existentes de unidad/regresión y las pruebas visuales locales se consideran cerradas para los escenarios ejecutados.

## 7. Decisión de alcance: rate limiting reservado para producción (23/11/2026)

**Decisión expresa del responsable:** el `rate limiting` distribuido y la protección perimetral asociada pertenecen a la **versión productiva**, no al criterio de aceptación del **MVP**. No deben impedir el **cierre de las pruebas locales del MVP** ni ocasionar infraestructura/costos adicionales para el ejercicio.

**Condiciones de MVP:** mantener controles existentes de token temporal, revocación, aislamiento por pedido, protección de datos y acceso del operador; pruebas y demostraciones con pedidos sintéticos en entorno controlado. La prueba de integración HTTP simulada pasó y no equivale a despliegue E2E.

**Reserva de seguridad:** retirar la condición de rate limiting del *gate del MVP* no autoriza abrir el endpoint a tráfico público irrestricto. El feature gate de seguimiento permanece desactivado en el despliegue actual; antes de exponerlo a usuarios externos debe existir una decisión de riesgo y controles adecuados a esa exposición. Rate limiting distribuido, endurecimiento perimetral y su validación HTTP 429 se transfieren al backlog de producción.

**Pendientes del MVP no relacionados con rate limiting:** consolidar las ramas de implementación en GitHub, comprobar integración del frontend/gateway/backend en escenario controlado (más allá de mocks), comparación final con el prototipo y cerrar evidencia de aceptación.
