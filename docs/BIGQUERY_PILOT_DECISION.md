# ADR-05-BQ — HISTÓRICO / SUPERADO por Firestore Standard
**Decisión histórica (01-nov-2026), NO vigente.** Ver [ADR-05-FS](FIRESTORE_STANDARD_MVP.md). **Propuesta anterior:** sustituir PostgreSQL/Cloud SQL por BigQuery en el MVP universitario SmartRoute AI, porque se esperan datos sintéticos, pocas sesiones y baja frecuencia de cambios. Esta decisión NO certifica que BigQuery sea mejor para logística productiva.

## Evaluación
| Factor | BigQuery piloto | Cloud SQL PostgreSQL | Riesgo |
|---|---|---|---|
| Costos fijos | No requiere instancia SQL permanente | Instancia facturable | BigQuery cobra consultas, almacenamiento y ciertas escrituras; no afirmar costo cero |
| Modelo | Analítico/columnar | OLTP transaccional | BigQuery no es un motor ideal para cambios de estado frecuentes |
| Integridad | PK/FK no se imponen automáticamente | Restricciones y transacciones OLTP | Duplicidad y referencias inválidas deben detectarse fuera del motor |
| Concurrencia | DML con cuotas/colas y conflictos | Mejor alineado a transacciones operacionales | Restringir piloto a baja concurrencia |
| KPI | Analítica directa SQL | Requiere consultas/agregación | BigQuery favorece evaluación académica |

**Fuente:** [Precios BigQuery](https://cloud.google.com/bigquery/pricing), [PK/FK no enforced](https://cloud.google.com/bigquery/docs/primary-foreign-keys), [DML y concurrencia](https://cloud.google.com/bigquery/docs/data-manipulation-language).

## Diseño de escrituras
- Tablas de estado `delivery_orders`, `delivery_routes` solo con pocas operaciones controladas; utilizar `MERGE`/DML parametrizado y versiones lógicas, y verificar filas afectadas. Los checks deben probar conflictos reales.
- Eventos `order_status_events` son append-only, con `event_id` y `idempotency_key`. BigQuery NO garantiza por sí solo unicidad o exactly-once. En demo evitar múltiples escritores simultáneos y conciliar duplicados; si requiere concurrencia real, reconsiderar Firestore o Cloud SQL.
- GPS: muestreo acotado, no streaming intensivo; no registrar coordenadas reales sin autorización y política de retención.
- Para el piloto preferir datasets sintéticos, carga por lotes o inserciones de bajo volumen; etiquetar `data_origin`.
- Las consultas de eventos GPS deberán incluir filtro de partición por `received_at`.
- Usar `google-cloud-bigquery` desde service account de Cloud Run con IAM mínimo y `maximum_bytes_billed`; fijar presupuestos/alertas (no constituyen límite duro de gasto).

## Reglas técnicas de aceptación
1. `bq query --use_legacy_sql=false < db/bigquery_schema.sql` crea tablas en proyecto y localización preconfigurados.
2. AC-003 asignación duplicada y AC-016 reintentos se prueban con 1 y múltiples clientes; **si fallan, NO promover** como plataforma multiusuario.
3. P95 de respuestas CRUD debe medirse nuevamente; consultas BigQuery pueden exceder la meta previa de <1 s. Registrar latencia real, no prometerla.
4. Cálculos y evidencia del piloto siguen distinguiendo observación/simulación/estimación.
5. Antes de cualquier uso productivo, reabrir ADR-05 y evaluar Firestore/Cloud SQL.

## Impacto documental
`db/schema.sql` queda como legado **no vigente**; el nuevo DDL es `db/bigquery_schema.sql`. El Charter/SDD v1 y el informe UPN previo documentan PostgreSQL como decisión histórica: actualizar sus próximas versiones y el Business Case con un recálculo, sin reescribir retrospectivamente el informe presentado.
