# SmartRoute AI — instrucciones para desarrollo asistido
Leer en orden: `specs/SPEC.md`, `docs/SDD_TRACEABILITY.md`, `docs/ADR.md`, `specs/openapi.yaml`, `tests/acceptance.feature`. Patrón de referencia: [DevPattern Assisted Agentic SDLC](https://github.com/JuliusCordova/DevPattern/tree/main/patterns/assisted-agentic-sdlc).

## Principios
1. El entregable Capstone es SOFTWARE desplegable (Android + dashboard + API + rutas + KPI). Agentes de desarrollo son herramientas; la IA operacional es asistente A1 y no optimiza rutas.
2. Spec → contrato → prueba → código → CI → revisión humana → staging → smoke → evidencia. Nunca escribir comportamiento fuera de SPEC sin propuesta de modificación.
3. Cada PR cita US, RF, AC, NEC, OE y aporta evidencia comprobable. No equiparar archivos de diseño con funcionalidad terminada.
4. Mantener monolito FastAPI modular y puertos para Maps, Firestore y Gemini; OR-Tools determinista. No GraphRAG, A2A, MCP de red ni multiagentes remotos por defecto.
5. Los agentes no hacen merge, despliegue, gasto ni cambios IAM de forma autónoma. Se requiere autorización humana y gates.
6. No introducir claves, datos personales reales ni GPS en código, prompts, logs ni fixtures. Todo uso simulado se identifica como tal.
7. Durante el primer slice, usar mocks/fixtures; no afirmar conexión a Maps/Firestore/Vertex sin evidencia.
8. Herramientas de desarrollo leen el contrato en `agents/contracts/` y las políticas en `policies/`; el enforcement real es CI, revisión y IAM, no el prompt.
9. Ejecutar `python -m pytest -q` (dentro de `services/api`) y build Docker antes de declarar listo. Registrar salida real en evidencias.
10. Deploy Cloud Run condicionado a credenciales y proyecto configurados por el equipo; no publicar servicios sin revisión.

## Roles humanos/assistidos
Coordinator, SDD, Architect, Backend, Frontend, QA y DevOps. Pueden trabajar como funciones o agentes ADK, sin infraestructura de agentes adicional obligatoria. Separar build-time de runtime.
