# Corte de SmartRoute AI — Android, operador y DEF-01 (24/11/2026)

**Proyecto:** SmartRoute AI — Capstone UPN. **Rama de trabajo:** `test/us016-integracion`. **Fecha del corte:** 24/11/2026 (hora Perú). **Fuente:** salidas de PowerShell y capturas del emulador Android y del panel de operadores aportadas en la sesión de validación. **Decisión:** detener el trabajo aquí y conservar el estado; no hacer merge a `main`.

## 1. Android repartidor — compilación, instalación y navegación

- En Windows, usando JDK 21 Eclipse Adoptium, `./gradlew.bat :app:assembleDebug --no-daemon` terminó **BUILD SUCCESSFUL in 53s**; 38 tareas (8 ejecutadas, 30 up-to-date).
- APK debug generado en `apps/driver-android/app/build/outputs/apk/debug/app-debug.apk`: **33 070 890 bytes**, fecha Windows **24/11/2026 22:04:49**.
- Emulador Android identificado como `emulator-5554`; `adb -s emulator-5554 install -r .../app-debug.apk` devolvió **Success**.
- Captura del listado **Mis rutas**: sesión identificada, ruta `fb413b71...` **Completada**, **5/5 paradas atendidas (100%)**, **4 entregadas y 1 no entregada**, 41,7 km / 61 min **estimados**.
- Captura del **detalle de ruta**: mapa OpenStreetMap, depósito y 5 paradas enumeradas, estados por pedido **Entregado / No entregado**, porcentaje de paradas atendidas y duración/distancia estimadas. La pantalla declara expresamente que la línea une paradas en orden y **no** representa trayecto vial calle por calle.
- **Alcance de la evidencia:** compilación, instalación, apertura, consulta y navegación al detalle en emulador **sí**; no afirmar ensayo completo en dispositivo físico ni todas las transiciones de entregas activas.

## 2. Panel operador en Cloud Run

- Panel `smartroute-web-staging` en URL `https://smartroute-web-staging-mkqutd4koq-uc.a.run.app`; revisión `00012-ztd` con 100% del tráfico, confirmado en CLI antes de esta sesión.
- Captura de dashboard autenticado: **23 pedidos**, **4 rutas**, **82,4% efectividad**, **14,8% mejora global estimada**; pipeline muestra **14 entregados**, **3 no entregados**, **6 asignados**.
- Captura de US-011 / **Rendimiento de las rutas** con tiempos y distancias **de matriz vial estimada** y fuentes indicadas. Tabla de 4 rutas, cifras verificadas visualmente:

| Ruta (prefijo) | Base (s) | Optimizada (s) | Mejora de tiempo presentada | Distancia base → optimizada |
|---|---:|---:|---:|---|
| `21e3de4b` | 3818 | 3350 | 12,26% | 40,43 km → 35,31 km |
| `681f7f60` | 1895 | 1526 | 19,47% | 18,49 km → 15,26 km |
| `aec305db` | 2178 | 1833 | 15,84% | 20,96 km → 16,8 km |
| `fb413b71` | 4284 | 3659 | 14,59% | 48,43 km → 41,68 km |

- Fórmula de mejora de tiempo: `100 * (baseline_seconds - optimized_seconds) / baseline_seconds`; los porcentajes observados coinciden con los segundos de las filas, redondeados a dos decimales.
- Captura de **Mapa de operaciones**: OpenStreetMap de Lima con puntos y ruta **persistida**, rótulo **«Ruta guardada · recorrido vial estimado»**. El panel **03 · Comparación** permanecía **«Pendiente de cálculo»** porque no se realizó nueva vista previa.
- Captura de **05 · Ruta persistida**: ruta `21e3de4b-4002-5870-bc4e-8eafb2826219` en estado COMPLETED, tiempo original 3818 s (64 min), optimizado 3350 s (56 min), **12,26% mejora estimada de tiempo**, distancias 40,43 km → 35,31 km, secuencia guardada, conductor asignado; sección **06 · Asignar conductor** muestra asignación y recorrido finalizado.
- En la lista de pedidos están visibles controles **Crear enlace** (US-016), cuya funcionalidad E2E principal se había confirmado en otra evidencia previa.

## 3. Cierre de defectos: interpretación estricta

**DEF-01 — Validación del cálculo actual: evidencia visual satisfactoria.** UI presenta segundos exactos, etiqueta explícita **mejora estimada de tiempo**, y cifras actuales aritméticamente consistentes. **No está auditada** la cifra histórica **19,43%** del caso del 15/11; no declarar cerrado ese dato específico sin JSON original con segundos/matriz.

**SEC-01 — Corrección de código y tests unitarios implementados, cierre E2E pendiente.** Confirmado en código `check_revoked=True` tanto en `services/gateway/app/main.py` como `services/api/app/auth.py`. Falta validar de forma controlada en staging que **un token real revocado** devuelve 401, sin tocar cuentas reales. Ver `docs/evidence/SEC01_FIREBASE_TOKEN_REVOCATION_2026-11-23.md`.

**Vista previa doble trazado (baseline vs optimizada): aún sin captura de aceptación.** La captura de mapa corresponde a ruta **guardada**; no se seleccionaron pedidos ni se solicitó nueva optimización, por lo que no equivale a prueba del overlay de dos rutas. No registrar ese paso como completado.

## 4. Git y alcance

- En PowerShell: `git fetch origin`, `git switch test/us016-integracion`, `git pull --ff-only origin test/us016-integracion` → **Already up to date** antes de este checkpoint; `git status -sb` mostró `?? .venv/` sin seguimiento. **Nunca agregar `.venv/` al repositorio.**
- US-012 Gemini, US-013/014 offline, US-015 piloto de campo y otras funciones excluidas permanecen **fuera del alcance de la entrega**. Ver decisión `docs/decisions/CR-2026-11-24-02_US012_US015_MEJORAS_FUTURAS.md`.
- Este commit **solo conserva la trazabilidad textual de resultados y capturas observadas en la conversación**; **no incorpora los archivos binarios de capturas ni el APK**. Para entregar evidencias visuales como archivos en GitHub hará falta agregarlas explícitamente desde el equipo local o el entorno donde residan.
- **Siguiente sesión:** completar controles de cierre sin repetir pruebas aprobadas, guardar evidencias visuales como archivos si se requieren para el informe, decidir bloqueantes y merge final solo con autorización.

**Fin del checkpoint.**
