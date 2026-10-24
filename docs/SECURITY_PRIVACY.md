# Seguridad, privacidad y control LLM — baseline
**Amenazas:** extracciones de ubicaciones y direcciones, escalamiento de roles, GPS no autorizado, key leakage, prompt injection, gasto excesivo de Maps/Vertex, datos falsos de KPI.
| Amenaza | Control técnico | Evidencia esperada |
|---|---|---|
| IDOR/rol | JWT/OIDC verificado y RBAC/ownership servidor | AC-001,004 y tests adversariales |
| GPS vigilancia | consentimiento explícito revocable, ruta ACTIVE, min. retención | AC-006,007 + auditoría |
| Exfiltración/PII | no PII a Gemini; minimización y logging scrub | golden cases, revisión de logs |
| Prompt injection | Gemini sin tools/write permisos; schema validation y no confiar en instrucciones de datos | AC-013,014, evals |
| Secretos | Secret Manager, IAM mínimo, WIF, sin keys en git | revisión CI, IAM checklist |
| Tráfico/API cost | quota caps, budgets, max 10 paradas, retries con backoff | pruebas quota/falla |
| Perdida conexión | idempotencia, cola P1, eventos UTC | AC-016 |

**Privacidad y consentimiento:** las coordenadas son datos personales potenciales. Configurar aviso y consentimiento informado en app; limitar finalidad, accesos y retención, eliminar según política, proteger datos de rutas y destinos. Revisar Ley 29733 y contratos GCP Maps/Vertex antes de ejecutar piloto real.

**Guardrails LLM:** entrada = KPI estructurados validados; salida = texto + caveats + action_taken=false. No herramientas, no DB write, no ejecución de instrucciones arbitrarias ni de archivos. Error de proveedor ⇒ mensaje determinista, nunca inventar mejora.

**Salida profesional:** reportar limitaciones y efectos no deseados (vigilancia, presión laboral, sesgo por zona), con mitigaciones; la mejora jamás se presupone real. Auditoría de acceso y del uso IA y prompts usados en el informe UPN.
