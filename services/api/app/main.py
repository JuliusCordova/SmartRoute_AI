"""Initial deployable health/readiness slice. Not yet a full SmartRoute business API."""
from fastapi import FastAPI

app = FastAPI(title="SmartRoute AI", version="0.1.0")

@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "smartroute-api"}

@app.get("/ready", tags=["health"])
def ready() -> dict[str, str]:
    # This currently checks process readiness ONLY, not external systems.
    return {"status": "ready", "scope": "process-only"}
