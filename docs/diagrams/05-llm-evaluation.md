# Flujo LLM — consulta segura y evaluación
```mermaid
flowchart TD
  U["Operador solicita explicación"] --> B["FastAPI: JWT / RBAC"]
  B --> Q["Consultar KPI agregados verificados"]
  Q --> G{"Datos suficientes?"}
  G -->|No| N["Respuesta: faltan datos / sin conclusión"]
  G -->|Sí| S["Minimizar payload, sin PII"]
  S --> V["Vertex AI Gemini (sin tools ni write credentials)"]
  V --> J["Validar JSON schema y magnitudes vs fuente"]
  J --> K{"Consistencia y seguridad"}
  K -->|Falla| F["Fallback determinista con incertidumbre"]
  K -->|Pasa| O["Explicación + KPI de origen + advertencia"]
  O --> L["Logging sin PII"]
  F --> L
  N --> L
```
Prueba golden set: 20 casos (mejora negativa, n insuficiente, intento de modificación, prompt injection, datos ausentes, unidades). Objetivo: 0 KPI inventados, 0 cambios en DB, 0 filtraciones PII. IA no sustituye a OR-Tools ni gobierna permisos.
