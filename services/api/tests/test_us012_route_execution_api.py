"""US-012 API contracts: only DRIVER may start their own route."""
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from app.auth import UserContext, require_driver
from app.main import app, get_route_execution_repository
from app.route_execution import RouteExecutionConflict, RouteExecutionMissing


class FakeExecution:
    def __init__(self):
        self.calls = []
        self.result = None
        self.failure = None

    def start(self, *, driver_uid, payload):
        self.calls.append((driver_uid, payload))
        if self.failure:
            raise self.failure
        from app.route_execution import RouteExecutionResult
        if self.result is None:
            self.result = RouteExecutionResult(
                id="synthetic-route", driver_id=driver_uid, status="ACTIVE",
                version=payload.expected_version + 1,
                started_at=datetime.now(timezone.utc),
            )
        return self.result


def start_body():
    return {"expected_version": 2, "idempotency_key": str(uuid4())}


def test_only_authenticated_driver_can_start_and_payload_has_no_route_id():
    fake = FakeExecution()
    app.dependency_overrides[require_driver] = lambda: UserContext(
        uid="synthetic-driver", role="DRIVER")
    app.dependency_overrides[get_route_execution_repository] = lambda: fake
    try:
        with TestClient(app) as client:
            r = client.post("/api/v1/driver/me/route/start", json=start_body())
            assert r.status_code == 200, r.text
            assert r.json()["status"] == "ACTIVE"
            assert r.json()["version"] == 3
            assert fake.calls[0][0] == "synthetic-driver"
            assert client.post("/api/v1/driver/me/route/start",
                               json={**start_body(), "driver_id": "other"}).status_code == 422
            assert client.post("/api/v1/driver/me/route/start",
                               json={"expected_version": 0,
                                     "idempotency_key": str(uuid4())}).status_code == 422
            assert len(fake.calls) == 1
    finally:
        app.dependency_overrides.clear()


def test_start_propagates_safe_not_found_conflict_and_storage_errors():
    fake = FakeExecution()
    app.dependency_overrides[require_driver] = lambda: UserContext(
        uid="synthetic-driver", role="DRIVER")
    app.dependency_overrides[get_route_execution_repository] = lambda: fake
    try:
        with TestClient(app) as client:
            for failure, code in (
                (RouteExecutionMissing("No assigned route"), 404),
                (RouteExecutionConflict("Route version changed"), 409),
                (RuntimeError("internal error"), 503),
            ):
                fake.failure = failure
                r = client.post("/api/v1/driver/me/route/start", json=start_body())
                assert r.status_code == code, r.text
                assert "internal error" not in r.text
    finally:
        app.dependency_overrides.clear()


def test_start_requires_firebase_and_driver_role():
    body = start_body()
    with TestClient(app) as client:
        assert client.post("/api/v1/driver/me/route/start", json=body).status_code == 401
    from fastapi import HTTPException
    app.dependency_overrides[require_driver] = lambda: (_ for _ in ()).throw(
        HTTPException(status_code=403, detail="Driver role required"))
    try:
        with TestClient(app) as client:
            assert client.post("/api/v1/driver/me/route/start", json=body).status_code == 403
    finally:
        app.dependency_overrides.clear()
