# Evidencia de QA Automation #6 — SmartRoute AI

**Proyecto:** UPN Capstone / SmartRoute AI  
**Estado:** QA automatizado 4/4 aprobado en la ejecución #6, según capturas del workflow y los reportes JUnit adjuntados para revisión.  
**Commit bajo prueba:** [`70cd7c59f67f3bb991133028bfe54a36a4c39de4`](https://github.com/JuliusCordova/SmartRoute_AI/commit/70cd7c59f67f3bb991133028bfe54a36a4c39de4)  
**Rama:** `feat/mobile-driver-android-base` · **PR:** [#56](https://github.com/JuliusCordova/SmartRoute_AI/pull/56) (no fusionado).  
**Workflow:** [SmartRoute QA Automation](https://github.com/JuliusCordova/SmartRoute_AI/actions/workflows/qa-automation.yml).  
**Fecha de ejecución:** 20/21 de noviembre de 2026 (zona horaria según GitHub / Lima; no inferir hora exacta desde el JUnit).

## 1. Resultado del gate

| Job | Evidencia observada | Resultado |
| --- | --- | --- |
| Backend + Firestore Emulator | Job verde; `qa-backend-firestore-junit.zip` | PASS (97 aprobadas, 1 omitida) |
| Gateway auth + routing | Job verde; `qa-gateway-junit.zip` | PASS (24 aprobadas) |
| Android JVM + debug APK | Job verde; `qa-android-junit.zip`; log Gradle | PASS (42 aprobadas) |
| Operator React build | Job verde; compilación React y Docker en workflow | PASS (build, no JUnit) |
| QA gate summary | Job verde en ejecución #6 | PASS |

**Total de tests reportados en los tres conjuntos JUnit:** 164; **163 aprobados**, **0 fallos**, **0 errores** y **1 omitido**. Estos totales no incluyen el build web como prueba unitaria.

## 2. Desglose reproducible de XML

### Android — 42/42

| Suite XML | Tests | Fallos | Errores | Omitidas |
| --- | ---: | ---: | ---: | ---: |
| `DeliveryWorkflowTest` | 8 | 0 | 0 | 0 |
| `DomainTest` | 5 | 0 | 0 | 0 |
| `DriverRouteContractTest` | 17 | 0 | 0 | 0 |
| `RepositoryTest` | 7 | 0 | 0 | 0 |
| `ViewModelTest` | 5 | 0 | 0 | 0 |
| **Total Android** | **42** | **0** | **0** | **0** |

El log de `Test and assemble local-only debug build` muestra Gradle **9.3.1**, ` :app:testDebugUnitTest` y `:app:assembleDebug`, concluyendo **BUILD SUCCESSFUL in 2m 44s**, 43 tareas ejecutadas. Se observó la advertencia no bloqueante sobre `libandroidx.graphics.path.so`, empaquetada sin strip de símbolos. La tarea `assembleDebug` confirma compilación del APK debug; **no** se ha probado instalación, arranque o interacción en un equipo físico en esta ejecución.

### Backend + Firestore Emulator — 98 pruebas declaradas

- 97 aprobadas, 0 fallos, 0 errores, 1 omitida.
- Omitida: `tests.test_driver_workflow_firestore_emulator::test_emulator_is_required_for_workflow_integration`, razón JUnit: **`Emulator available`**.
- El workflow define `GOOGLE_CLOUD_PROJECT=demo-smartroute`, `FIREBASE_PROJECT_ID=demo-smartroute`, `FIRESTORE_EMULATOR_REQUIRED=1` y ejecuta tests mediante `firebase emulators:exec --only firestore`. Por diseño, este gate no escribe en la instancia Firestore real.

### Gateway — 24/24

Reporte `gateway-junit.xml`: 24 tests, 0 fallos, 0 errores, 0 omitidos.

## 3. Problema de CI y resolución

- Ejecuciones previas: Android fallaba en preparación del SDK, primero por paquete legado `tools` solicitado durante `android-actions/setup-android@v3`, luego por `sdkmanager: command not found`.
- [Commit `e6c7371`](https://github.com/JuliusCordova/SmartRoute_AI/commit/e6c73712ae14d65c195a853d50da5e5eee8501b5): suprime setup-android heredado y utiliza el SDK del runner.
- [Commit `70cd7c5`](https://github.com/JuliusCordova/SmartRoute_AI/commit/70cd7c59f67f3bb991133028bfe54a36a4c39de4): localiza `sdkmanager` dentro de `ANDROID_HOME`, sin depender de `PATH`.
- La ejecución #6 terminó con gate verde después de esa corrección.

## 4. Trazabilidad de artefactos

Los ZIP JUnit se descargaron de la sección **Artifacts** de la ejecución #6 y se inspeccionaron para este registro. Nombres:

- `qa-android-junit.zip` — cinco XML de suites JVM.
- `qa-backend-firestore-junit.zip` — `backend-junit.xml`.
- `qa-gateway-junit.zip` — `gateway-junit.xml`.

**Retención:** el workflow configura `retention-days: 14` para artefactos; por ello se documentan aquí los resultados y el enlace al workflow. Los ZIP originales no se han incorporado a Git: este registro no debe interpretarse como custodia permanente de bytes adjuntos. Se recomienda respaldarlos en la gestión de evidencias del curso si se exige conservación.

## 5. Alcance y pendientes de aceptación

**Confirmado:** los cuatro jobs del CI finalizaron exitosamente; pruebas JVM Android, pruebas backend sobre emulador y gateway finalizaron sin fallos; compilación de Android debug y build web aprobados.

**No demostrado por este gate:** ejecución Android en dispositivo/emulador gráfico, login real con Firebase, flujo Android → Gateway Cloud Run → API → Firestore real de staging, matriz de permisos de entorno desplegado, disponibilidad operacional, medición de tiempos/KPIs del piloto o reducción real del 20 %.

**Controles de continuidad:**
1. Mantener PR #56 sin merge hasta aprobación expresa y revisión de integración.
2. No dirigir el QA automatizado a Firestore productivo ni a las bases `(default)`/`gestioncitas` del proyecto compartido.
3. Mantener revisiones QA con 0 % de tráfico principal; no efectuar despliegue desde este registro documental.
4. Siguiente gate separado: pruebas integradas de staging, con autorización explícita y evidencia independiente.

## 6. Criterio de cierre

**Gate CI automatizado: APROBADO (4/4).** El cierre de este gate no constituye cierre del MVP ni autorización de merge, promoción a producción o aceptación del piloto académico.
