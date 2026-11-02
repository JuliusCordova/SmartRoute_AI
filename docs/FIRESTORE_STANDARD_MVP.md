# ADR-05-FS — Firestore Standard como base operativa de SmartRoute AI
**Decisión aprobada para el Capstone (2026-11-01):** Firestore **Standard edition en Native mode**, una base de datos en el proyecto GCP del equipo. Sustituye el ADR-05-BQ (BigQuery) y el ADR-05 PostgreSQL. No se ha creado el recurso cloud ni desplegado infraestructura.

## Razón y alcance
- Piloto académico: 1 depósito, 1 conductor, 5–10 paradas/ruta, pocos usuarios, datasets sintéticos y períodos de uso cortos.
- Firestore evita una instancia relacional encendida y ofrece transacciones de documentos para asignaciones, estados e idempotencia que BigQuery no garantiza del mismo modo.
- Para minimizar servicios: **Firestore es la única base operativa**. Calcular indicadores a partir de documentos agregados por API y exportar CSV o JSON a archivos locales/Cloud Storage solo si se necesita. **BigQuery NO se provisiona** en el MVP.
- No presupuestar costo cero: leer/escribir, entradas de índice, almacenamiento y red pueden generar gastos. Cuotas gratis para **una** base por proyecto: 1 GiB, 50.000 lecturas/día, 20.000 escrituras/día, 20.000 eliminaciones/día y 10 GiB de egress/mes; ciertas funciones (TTL, PITR, backups administrados) se cobran.
- Si el proyecto GCP ya tiene una base gratuita, otra base puede no recibir la cuota. Verificar la región disponible y ubicación de Cloud Run. La selección de región, facturación y recursos requiere autorización del equipo.
- Fuentes: https://docs.cloud.google.com/firestore/quotas ; https://cloud.google.com/firestore/pricing ; https://firebase.google.com/docs/firestore/security/insecure-rules

## Colecciones — contrato lógico v1
| Colección | ID de documento | Contenido relevante |
|---|---|---|
| `users` | UID del proveedor de identidad | rol OPERATOR/DRIVER, active, created_at |
| `drivers` | UUID | user_id, gps_consent, consent_updated_at |
| `orders` | UUID | created_by, address_label, geo (lat/lng), due_at, status, version, route_id opcional |
| `routes` | UUID | driver_id, depósito, status, baseline_order, optimized_order, version, timestamps |
| `routes/{routeId}/stops` | orderId | baseline_sequence, optimized_sequence, status |
| `order_events` | clave estable de evento | order_id, actor_id, idempotency_key, old/new status, occurred_at, data_origin |
| `driver_locations` | driverId (última posición) | route_id, lat, lng, captured_at, received_at, accuracy, data_origin |
| `route_evaluations` | UUID | route_id, base/optimized seconds, source and fingerprint, calculated_at, data_origin |
| `incidents` | UUID | order_id, incident_type, created_at |

**No guardar GPS histórico continuo** para el piloto: `driver_locations/{driverId}` sobrescribe la última posición mientras la ruta está activa; muestreo inicialmente cada 60 s, configurable. Si el trabajo académico requiere historial, diseñar colección separada acotada con consentimiento y costo medido. No se usa TTL automático sin revisar su facturación.

## Consistencia y seguridad
1. `POST /orders`: UUID generado en servidor, coordenadas validadas y autorización OPERATOR comprobada antes de escribir.
2. Asignación: usar transacción Firestore que lee `orders/{id}` y `routes/{routeId}`, verifica `route_id` ausente, estado válido y conductor válido; actualiza documentos de manera atómica. Las transacciones pueden reintentarse; su callback no debe realizar side effects ni llamadas Maps/LLM.
3. Actualizar estado: mantener idempotencia mediante documento `order_events/{actorId}:{idempotencyKey}` creado dentro de la **misma transacción** que el cambio de pedido; reintentos devuelven resultado consistente, conflicto de payload con misma clave → 409.
4. GPS: el backend valida UID/rol/conductor, consentimiento vigente y ruta ACTIVE antes de sobrescribir ubicación; al finalizar la ruta deja de aceptar GPS y planifica purga; no enviar PII a Gemini.
5. **Acceso a Firestore solo desde FastAPI** en Cloud Run mediante Admin/server SDK con IAM mínimo. Los clientes Android y React no acceden a Firestore directamente. Las reglas Firestore son `deny all` para accesos directos; **las bibliotecas de servidor omiten esas reglas**, por lo que RBAC en API e IAM son controles obligatorios.
6. Paginar y filtrar por conductor/estado; evitar listeners abiertos, lecturas de colecciones completas y N+1 queries. Documentos e índices mantienen el costo controlado.
7. Almacenar `data_origin=synthetic/observed/estimated` de forma explícita y separar métricas; no dar por demostrado el objetivo de reducción del 20 %.

## Criterios de aceptación
- AC-002 coordenadas inválidas no crean documento.
- AC-003 dos asignaciones al mismo pedido → exactamente una confirmada; la otra 409.
- AC-016 reenvío de `Idempotency-Key` → un evento lógico y estado estable.
- AC-006 GPS sin consentimiento o fuera de ruta ACTIVE → 403 sin escritura.
- AC-012 KPI correctos con fixtures; prueba de número de lecturas bajo lote piloto.
- Contratos de integración probados con Firestore Emulator o dobles, más smoke real antes de afirmar GCP DEPLOYED.

## Costos y límites operativos
Cloud Run min instances=0, Firestore una única base Standard, peticiones sin polling agresivo; Routes API solo al solicitar optimización, OR-Tools local en API y Gemini sólo ante petición de explicación; no mantener BigQuery, Cloud SQL, GKE, Redis ni ADK runtime adicional por defecto. Cloud Billing budget/alerts NO es un límite duro; controlar cuotas cuando sea posible.

## Revisión del informe UPN
Los documentos históricos que citan PostgreSQL o BigQuery quedan como decisiones ya superadas; no reescribir informes entregados. Actualizar el capítulo de arquitectura/Business Case y trazabilidad en la próxima versión y registrar evidencia de costos reales.
