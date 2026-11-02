# Orquestación asistida SDD — contrato, no runtime desplegado

Para el Capstone se utilizará un orquestador de trabajo humano/IA con especialistas SDD, arquitectura, backend, frontend, QA y DevOps. `AGENTS.md` y los contratos definen cómo colaborar. **No existe todavía un agente ADK desplegado**; los contratos permiten implementarlo cuando aporte valor.

## Flujo mínimo
Solicitud/US → SDD revisa SPEC y aceptación → Arquitecto revisa ADR → Builder crea código/fixtures → QA reproduce tests y revisa seguridad → DevOps genera evidencia build/deploy → humano revisa PR y autoriza merge/deploy.

## Contratos
- [Coordinador](contracts/master.yaml)
- [Especialistas](contracts/specialists.yaml)

El Agent Contract es descriptivo; usar IAM, permisos de GitHub y controles CI para enforcement, no confiar en instrucciones del modelo. El primer objetivo es entregar una API real en Cloud Run y después añadir ADK para explicación consultiva cuando los tests del producto principal estén verdes.
