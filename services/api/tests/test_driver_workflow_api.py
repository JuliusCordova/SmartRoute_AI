"""US-012/013/014 HTTP and auth tests: no cloud IO; synthetic records only."""
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.auth import UserContext, require_driver
from app.main import app, get_driver_workflow_repository
from app.firestore_driver_workflow import WorkflowConflict, WorkflowMissing
from app.qa_write_guard import QaWriteGuardDenied


class FakeWorkflow:
    def __init__(self, error=None):
        self.error = error
        self.calls = []

    def execute(self, *, driver_uid, action, payload, order_id=None):
        self.calls.append((driver_uid, action, payload, order_id))
        if self.error:
            raise self.error
        receipt = {
            "id": "route-synthetic",
            "status": "COMPLETED" if action == "complete" else "ACTIVE",
            "version": payload.expected_version + 1,
        }
        if action in ("deliver", "fail"):
            receipt.update(
                order_id=order_id,
                order_status="DELIVERED" if action == "deliver" else "FAILED",
            )
        return receipt


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def setup(fake, uid="driver-qa-synthetic"):
    app.dependency_overrides[require_driver] = lambda: UserContext(uid=uid, role="DRIVER")
    app.dependency_overrides[get_driver_workflow_repository] = lambda: fake


@pytest.mark.parametrize("action,endpoint,body,expect", [
    ("start", "/api/v1/driver/me/route/start", {}, "ACTIVE"),
    ("deliver", "/api/v1/driver/me/route/stops/oid-1/deliver", {}, "DELIVERED"),
    ("fail", "/api/v1/driver/me/route/stops/oid-1/fail", {"reason": "Local cerrado"}, "FAILED"),
    ("complete", "/api/v1/driver/me/route/complete", {}, "COMPLETED"),
])
def test_driver_actions_use_verified_uid_and_return_strict_receipts(action, endpoint, body, expect):
    fake = FakeWorkflow()
    setup(fake)
    key = str(uuid4())
    response = TestClient(app).post(endpoint, json={
        "expected_version": 2, "idempotency_key": key, **body,
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["version"] == 3
    assert data.get("order_status", data["status"]) == expect
    uid, called_action, payload, oid = fake.calls[0]
    assert uid == "driver-qa-synthetic" and called_action == action
    assert str(payload.idempotency_key) == key
    assert oid == ("oid-1" if action in ("deliver", "fail") else None)


@pytest.mark.parametrize("endpoint", [
    "/api/v1/driver/me/route/start",
    "/api/v1/driver/me/route/stops/oid-1/deliver",
    "/api/v1/driver/me/route/stops/oid-1/fail",
    "/api/v1/driver/me/route/complete",
])
def test_anonymous_driver_actions_denied(endpoint):
    r = TestClient(app).post(endpoint, json={
        "expected_version": 2, "idempotency_key": str(uuid4()), "reason": "Puerta cerrada",
    })
    assert r.status_code == 401


def test_operator_cannot_execute_driver_actions():
    def deny():
        raise HTTPException(403, "Driver role required")
    app.dependency_overrides[require_driver] = deny
    r = TestClient(app).post("/api/v1/driver/me/route/start", json={
        "expected_version": 2, "idempotency_key": str(uuid4()),
    })
    assert r.status_code == 403


@pytest.mark.parametrize("error,status", [
    (WorkflowMissing("Stop absent"), 404),
    (WorkflowConflict("Stale version"), 409),
    (QaWriteGuardDenied("Guard rejected"), 403),
    (ValueError("Reason required"), 422),
    (RuntimeError("Emulator offline"), 503),
])
def test_workflow_error_mapping(error, status):
    fake = FakeWorkflow(error=error)
    setup(fake)
    r = TestClient(app).post("/api/v1/driver/me/route/start", json={
        "expected_version": 2, "idempotency_key": str(uuid4()),
    })
    assert r.status_code == status


@pytest.mark.parametrize("patch", [
    {"expected_version": 0},
    {"idempotency_key": "invalid-uuid"},
    {"other_field": "not-allowed"},
])
def test_invalid_payload_rejected(patch):
    setup(FakeWorkflow())
    body = {"expected_version": 2, "idempotency_key": str(uuid4())}
    body.update(patch)
    r = TestClient(app).post("/api/v1/driver/me/route/start", json=body)
    assert r.status_code == 422


def test_failure_reason_missing_rejected_by_workflow():
    setup(FakeWorkflow(error=ValueError("Failure reason required")))
    r = TestClient(app).post("/api/v1/driver/me/route/stops/oid-1/fail", json={
        "expected_version": 2, "idempotency_key": str(uuid4()),
    })
    assert r.status_code == 422
