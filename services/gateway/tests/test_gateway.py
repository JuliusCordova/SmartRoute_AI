"""Gateway security contract: no IAM token to caller; reject invalid tokens/routes."""
import os
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.main import app, PRIVATE_API_URL

client = TestClient(app)
ENV = {
    "GOOGLE_CLOUD_PROJECT": "proyectopersonal-480420",
    "SMARTROUTE_BACKEND_URL": PRIVATE_API_URL,
    "SMARTROUTE_GATEWAY_ENABLED": "true",
    "SMARTROUTE_ALLOWED_ORIGINS": "https://example.org",
}


def test_health_is_public_without_claiming_backend_readiness():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "smartroute-gateway"


def test_fails_closed_when_not_configured():
    with patch.dict(os.environ, {}, clear=True):
        r = client.get("/api/v1/orders")
    assert r.status_code == 503


def test_missing_firebase_rejected_without_getting_iam_token():
    with patch.dict(os.environ, ENV), patch("app.main.private_id_token") as mint:
        r = client.get("/api/v1/orders")
    assert r.status_code == 401
    mint.assert_not_called()


def test_origin_is_rejected_before_minting_service_token():
    with patch.dict(os.environ, ENV), patch("app.main.private_id_token") as mint:
        r = client.get("/api/v1/orders", headers={"Origin": "https://attacker.example",
                                                   "Authorization": "Bearer fake"})
    assert r.status_code == 403
    mint.assert_not_called()


def test_unknown_endpoint_rejected():
    with patch.dict(os.environ, ENV):
        assert client.get("/api/v1/debug").status_code == 404
        assert client.get("/api/v1/routes").status_code == 404


def test_firebase_and_cloudrun_tokens_separated(monkeypatch):
    seen = {}

    async def fake_request(self, *, method, url, params, content, headers):
        seen.update({"method": method, "url": url, "headers": headers})
        import httpx
        return httpx.Response(201, json={"id": "synthetic"})

    with patch.dict(os.environ, ENV), \
         patch("app.main.auth.verify_id_token", return_value={"uid": "synthetic-user"}), \
         patch("app.main.firebase_app", return_value=object()), \
         patch("app.main.private_id_token", return_value="fake-google-id-token"), \
         patch("app.main.httpx.AsyncClient.request", new=fake_request):
        r = client.post("/api/v1/orders",
                        headers={"Authorization": "Bearer fake-firebase-token",
                                 "Origin": "https://example.org"},
                        json={"address_label": "Synthetic", "geo": {"latitude": -12, "longitude": -77}})
    assert r.status_code == 201
    assert seen["url"] == PRIVATE_API_URL + "/api/v1/orders"
    assert seen["headers"]["Authorization"] == "Bearer fake-firebase-token"
    assert seen["headers"]["X-Serverless-Authorization"] == "Bearer fake-google-id-token"
    assert "fake-google-id-token" not in r.text
    assert r.headers["access-control-allow-origin"] == "https://example.org"


def test_oversized_payload_rejected_before_iam():
    with patch.dict(os.environ, ENV), \
         patch("app.main.auth.verify_id_token", return_value={"uid": "user"}), \
         patch("app.main.firebase_app", return_value=object()), \
         patch("app.main.private_id_token") as mint:
        r = client.post("/api/v1/orders", headers={"Authorization": "Bearer fake"}, content=b"x" * 17000)
    assert r.status_code == 413
    mint.assert_not_called()


def test_preflight_allowed_origin_only():
    with patch.dict(os.environ, ENV):
        ok = client.options("/api/v1/orders",
            headers={"Origin": "https://example.org", "Access-Control-Request-Method": "POST"})
        assert ok.status_code == 204
        assert ok.headers["access-control-allow-origin"] == "https://example.org"
        bad = client.options("/api/v1/orders",
            headers={"Origin": "https://not-allowed.example", "Access-Control-Request-Method": "POST"})
        assert bad.status_code == 403
