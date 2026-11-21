"""US-012/013/014: edge allowlist, Firebase + IAM separation and tagged API routing.

No network, Firestore or Google Cloud calls: HTTP transport and identity mocked.
"""
import os
from unittest.mock import patch

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app, PRIVATE_API_URL

client = TestClient(app)
TAGGED_BACKEND = (
    "https://us014-backend-test---smartroute-api-staging-mkqutd4koq-uc.a.run.app"
)
ENV = {
    "GOOGLE_CLOUD_PROJECT": "proyectopersonal-480420",
    "SMARTROUTE_BACKEND_URL": TAGGED_BACKEND,
    "SMARTROUTE_GATEWAY_ENABLED": "true",
    "SMARTROUTE_ALLOWED_ORIGINS": "https://example.org",
}


@pytest.mark.parametrize("path", [
    "/api/v1/driver/me/route/start",
    "/api/v1/driver/me/route/complete",
    "/api/v1/driver/me/route/stops/synthetic-order-1/deliver",
    "/api/v1/driver/me/route/stops/synthetic-order-1/fail",
])
def test_driver_mutations_require_firebase_before_iam(path):
    with patch.dict(os.environ, ENV), patch("app.main.private_id_token") as mint:
        response = client.post(path, json={
            "expected_version": 2, "idempotency_key": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        })
    assert response.status_code == 401
    mint.assert_not_called()


@pytest.mark.parametrize("path", [
    "/api/v1/driver/me/route/start",
    "/api/v1/driver/me/route/complete",
    "/api/v1/driver/me/route/stops/synthetic-order-1/deliver",
    "/api/v1/driver/me/route/stops/synthetic-order-1/fail",
])
def test_driver_mutations_forward_to_only_approved_tag(path):
    observed = {}

    async def fake_request(self, *, method, url, params, content, headers):
        observed.update(method=method, url=url, headers=headers, content=content)
        return httpx.Response(409, json={"detail": "Synthetic version conflict"})

    with patch.dict(os.environ, ENV), \
         patch("app.main.auth.verify_id_token", return_value={"uid": "synthetic-driver"}), \
         patch("app.main.firebase_app", return_value=object()), \
         patch("app.main.private_id_token", return_value="mock-iam-token"), \
         patch("app.main.httpx.AsyncClient.request", new=fake_request):
        response = client.post(path, headers={"Authorization": "Bearer fake-firebase-token"}, json={
            "expected_version": 2, "idempotency_key": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        })
    assert response.status_code == 409
    assert observed["url"] == TAGGED_BACKEND + path
    assert observed["headers"]["Authorization"] == "Bearer fake-firebase-token"
    assert observed["headers"]["X-Serverless-Authorization"] == "Bearer mock-iam-token"
    assert "mock-iam-token" not in response.text


@pytest.mark.parametrize("backend", [
    "https://attacker.example",
    "http://127.0.0.1:8080",
    "https://us014-backend-test---smartroute-api-staging-mkqutd4koq-uc.a.run.app.evil.example",
])
def test_reject_unapproved_backend_before_firebase_or_iam(backend):
    env = {**ENV, "SMARTROUTE_BACKEND_URL": backend}
    with patch.dict(os.environ, env), patch("app.main.private_id_token") as mint:
        response = client.get("/api/v1/driver/me/route")
    assert response.status_code == 503
    mint.assert_not_called()


def test_reject_other_driver_and_unknown_paths():
    with patch.dict(os.environ, ENV):
        assert client.post("/api/v1/driver/another/route/start").status_code == 404
        assert client.post("/api/v1/driver/me/route/stops/a/b/deliver").status_code == 404
        assert client.put("/api/v1/driver/me/route/start").status_code == 404


def test_driver_mutation_preflight_restricted_origin():
    headers = {"Origin": "https://example.org", "Access-Control-Request-Method": "POST"}
    with patch.dict(os.environ, ENV):
        ok = client.options("/api/v1/driver/me/route/stops/synthetic-1/fail", headers=headers)
        denied = client.options("/api/v1/driver/me/route/start", headers={
            **headers, "Origin": "https://not-allowed.example",
        })
    assert ok.status_code == 204
    assert denied.status_code == 403


def test_iam_audience_is_canonical_even_for_tagged_target():
    seen = {}
    with patch("app.main.id_token.fetch_id_token", side_effect=lambda request, audience: seen.setdefault("audience", audience) or "fake") as fetch:
        from app.main import private_id_token
        private_id_token()
    assert seen["audience"] == PRIVATE_API_URL
