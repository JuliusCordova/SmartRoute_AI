# Punto de retorno — SmartRoute AI — 20 noviembre 2026

**Estado:** PAUSA SOLICITADA. Reanudar paso a paso, una comprobación por turno.  
**Rama de trabajo:** `feat/mobile-driver-android-base` · [PR #56](https://github.com/JuliusCordova/SmartRoute_AI/pull/56), **NO MERGE**.  
**Evidencia de QA:** [QA #6](QA_AUTOMATION_RUN_6_2026-11-20.md), commit probado `70cd7c5`, documento registrado en `b00830e`.

## 1. Último punto validado

- QA Automation #6: backend + Firestore Emulator, gateway, Android JVM/debug APK y operador React exitosos; resumen de gate aprobado.
- JUnit: 164 casos declarados, 163 aprobados, 1 omitido, 0 fallos, 0 errores (Android 42; backend 97+1 omitido; gateway 24).
- Android compilación `:app:testDebugUnitTest :app:assembleDebug`: Gradle 9.3.1, BUILD SUCCESSFUL, 43 tareas.
- La documentación de evidencia de QA quedó versionada en la rama del PR.
- **NO se ha ejecutado todavía el inventario de Cloud Run del siguiente paso**, ni probado integración Android → Gateway → API → Firestore real.

## 2. Punto exacto de reanudación

**Paso pendiente #1: inventario Cloud Run SOLO LECTURA desde Google Cloud Shell.** Solicitar al usuario ejecutar y compartir resultado:

```bash
gcloud run services list \
  --project=proyectopersonal-480420 \
  --region=us-central1 \
  --format="table(metadata.name,status.url,status.latestReadyRevisionName)"
```

Revisar salida y reconocer las revisiones para staging; no confundir servicios existentes con despliegues QA nuevos. Seguir **uno por uno**. Luego revisar (solo lectura) revisiones, IAM, URL/health y parámetros seguros; antes de cualquier prueba con escrituras reales, pedir aprobación específica, delimitar dataset de prueba y costo. No declarar E2E validado hasta contar con evidencia.

## 3. Restricciones no negociables

- No hacer merge del PR #56 sin aprobación humana; la rama sigue siendo área de trabajo.
- Revisiones QA con **0 % de tráfico principal**; no cambiar routing Cloud Run.
- No escribir automáticamente en Firestore real. No usar jamás las bases `(default)` o `gestioncitas`; `smartroute` es la base designada solo cuando proceda y sea autorizado.
- No desplegar ni cambiar IAM/facturación en el paso de inventario.
- No confundir CI verde con aceptación E2E, piloto real, mejoras del 20 % o release a producción.

## 4. Estimación orientativa de avance

**Avance global estimado: 60 % (rango de incertidumbre 50–65 %), NO métrica certificada ni porcentaje contractual.**

| Dimensión | Peso supuesto | Avance estimado | Contribución |
| --- | ---: | ---: | ---: |
| Especificación/arquitectura/trazabilidad SDD | 15 % | 90 % | 13.5 pp |
| API/backend y persistencia en pruebas controladas | 20 % | 85 % | 17.0 pp |
| Android / lógica DRIVER y build | 15 % | 75 % | 11.25 pp |
| Operador React / build y flujos | 10 % | 75 % | 7.5 pp |
| Integración real, seguridad y staging E2E | 20 % | 35 % | 7.0 pp |
| Piloto, KPIs, evidencia académica y cierre | 20 % | 15 % | 3.0 pp |
| **Total ponderado** | **100 %** | | **59.25 % (~60 %)** |

**Método:** ponderación gerencial provisional basada en el [plan de siete semanas](../PLAN_DESARROLLO_7_SEMANAS.md) y en el QA #6; los porcentajes por dimensión son juicios de avance, no conteos auditados de historias cerradas. El plan de siete semanas contiene referencias tecnológicas/US históricas (p. ej. Flutter frente a Android Kotlin/Compose implementado) y estados desactualizados: se requerirá reconciliar backlog con el código y los criterios de aceptación antes de reportar una cifra formal. El **gate CI** sí está **100 % aprobado (4/4)**, una dimensión distinta del **avance global ~60 %**.

## 5. Reanudar sin perder contexto

Mensaje recomendado: «Retomemos SmartRoute desde el checkpoint del 20-11-2026, paso inventario Cloud Run. Te comparto el resultado del comando».  
Una vez revisado el inventario, avanzar al siguiente único paso con evidencia observable.
