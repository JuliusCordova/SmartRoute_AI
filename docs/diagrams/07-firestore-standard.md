# Diagrama de componentes — Firestore Standard
```mermaid
flowchart TB
  Android["Flutter Android: repartidor"]
  Web["React: operador"]
  Auth["Emisor OIDC / Firebase Auth"]
  subgraph GCP["Google Cloud — piloto académico"]
    API["Cloud Run FastAPI, min instances=0"]
    FS[("Firestore Standard / Native mode")]
    SOL["OR-Tools, determinista"]
    AI["Gemini en Vertex AI, A1 / solo lectura"]
    LOG["Cloud Logging, IAM y presupuestos"]
  end
  MAPS["Google Routes API"]
  Android -->|"HTTPS JWT"| API
  Web -->|"HTTPS JWT"| API
  Android -.-> Auth
  Web -.-> Auth
  API -->|"Admin SDK, IAM mínimo"| FS
  API --> SOL
  SOL -->|"costos de viaje por adaptador API"| MAPS
  API -->|"KPI minimizados, por solicitud"| AI
  API --> LOG
```
La autorización del usuario se verifica en la API, incluso cuando el Admin SDK tenga acceso a Firestore. Android y React nunca disponen de credenciales de servicio. BigQuery y Cloud SQL no forman parte de la arquitectura activa del piloto.
