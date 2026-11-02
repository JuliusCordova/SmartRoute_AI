from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "smartroute-api"}

def test_ready_is_process_only():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["scope"] == "process-only"

def test_openapi_exists():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "/health" in response.json()["paths"]
