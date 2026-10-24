# Diagrama C4 simplificado — componentes GCP
```mermaid
flowchart TB
  subgraph USERS["Usuarios"]
    D["Repartidor: Flutter Android"]
    O["Operador: React Dashboard"]
  end
  subgraph GCP["Google Cloud"]
    I["OIDC / Firebase Auth (opción)"]
    CR["Cloud Run — FastAPI modular"]
    DB[("Cloud SQL: PostgreSQL")]
    SM["Secret Manager / IAM"]
    LG["Cloud Logging y Monitoring"]
    AR["Artifact Registry + CI/CD WIF"]
    V["Vertex AI: Gemini consultivo"]
    subgraph DOMAIN["Módulos dentro de Cloud Run"]
      P["Pedidos / Autorización"]
      R["Optimización OR-Tools"]
      T["GPS / eventos"]
      A["KPI / evaluaciones"]
      E["Explicaciones: JSON validado"]
    end
  end
  M["Google Maps Platform: Routes API"]
  D -->|"HTTPS + bearer"| CR
  O -->|"HTTPS + bearer"| CR
  D -.-> I
  O -.-> I
  CR --> P & R & T & A & E
  P --> DB
  T --> DB
  A --> DB
  R --> M
  R --> DB
  E -->|"solo KPI agregados"| V
  CR --> SM
  CR --> LG
  AR -->|"deploy"| CR
```
**Alcance:** un Cloud Run modular; las cajas de dominio NO son microservicios independientes. Vertex AI sólo recibe datos agregados minimizados. La API de Maps está fuera del perímetro GCP del proyecto aunque es servicio Google.
