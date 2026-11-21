# Integración segura de lo desarrollado — corte 21-11-2026

## Objetivo

Llevar a `main` artefactos revisados que no afecten el runtime, preservando el código QA en ramas de trabajo hasta completar controles para su promoción.

## Inventario verificado

| Componente | Estado de integración |
|---|---|
| Evidencias CI y recorrido Android QA | Integradas a `main` mediante PR #58 (squash `679e8fd`) |
| Operador web, órdenes y previsualización | El repositorio `main` ya contiene `apps/operator-web`; la prueba de cinco pedidos está documentada en `docs/EVIDENCIA_PILOTO_5_PEDIDOS_2026-11-15.md` |
| Android Kotlin / Jetpack Compose | Código en `feat/mobile-driver-android-base`, PR #56 abierto; no incluido en `main` |
| Backend/Gateway US-012 a US-014 | Cambios de desarrollo pendientes en PR #56; se han probado en revisiones US-014 separadas, no en tráfico principal |
| Prototipo UX antiguo | PR #52 abierto: incluye decisiones y referencias a Flutter desactualizadas; no fusionar a ciegas |

## Decisiones de integración

1. **Documentación:** incluir ADR-16 actualizado, con estado exacto de implementación Android.
2. **No merge de código PR #56** antes de separar cambios, revisar banderas QA y regresiones frente a `main`. Mantener revisiones Cloud Run etiquetadas sin tráfico principal.
3. **No merge directo de PR #52**: comprobar divergencias con decisiones de Kotlin/Firestore y recuperar solo elementos de UX todavía vigentes.
4. **Sin escrituras** en Firestore `smartroute`, `(default)` ni `gestioncitas`; sin cambios IAM, despliegues ni facturación.

## Condiciones de promoción de código (pendientes)

- Confirmar resultado actualizado de CI en la rama que se quiera integrar.
- Deshabilitar la función temporal `ENABLE_QA_WRITE_TEST` fuera del entorno QA y revisar lista de identidades/rutas fijas.
- Inspeccionar diferencias de 100+ archivos entre PR #56 y `main`; segmentar Android, backend/gateway y workflow en PRs revisables si corresponde.
- Ejecutar pruebas de regresión y de seguridad; documentar riesgos y rollback.
- Decisión humana separada antes de fusionar cambios de runtime y antes de cambiar tráfico de Cloud Run.

## Referencias

- [Corte para entrega UPN](evidence/CORTE_ENTREGA_UPN_2026-11-22.md)
- [Evidencia de cierre Android](evidence/US012_US013_US014_QA_FINAL_PASS_2026-11-21.md)
- [ADR-16](ADR-16-ANDROID-NATIVO.md)
