# PA-SDD assisted SDLC (build-time) ≠ SmartRoute runtime (product)

```mermaid
flowchart TB
    H["Human Capstone team"] --> M["Master / SDLC coordinator (assistive)"]
    M --> S["SDD analyst"] & A["Architect"] & B["Backend"] & F["Frontend"] & Q["QA"] & D["DevOps"]
    S & A --> V["SPEC / ADR / API / DB"]
    B & F --> C["Source code + fixtures"]
    Q --> T["Tests and evals"]
    D --> P["Docker / CI / deploy scripts"]
    V & C & T & P --> PR["GitHub PR"]
    PR --> G{"Human review + CI gate"}
    G -->|approved| DEP["Deploy Cloud Run staging"]
    G -->|rework| M
    DEP --> EV["Smoke + release evidence"]
```

Actual model: roles/contracts are documentation; ADK orchestration is **not implemented**. Runtime product remains FastAPI + OR-Tools, with optional Gemini A1.
