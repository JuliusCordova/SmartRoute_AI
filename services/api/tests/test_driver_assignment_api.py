"""US-011 API assignment role and error mapping tests; no Firestore calls."""
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.auth import UserContext, require_operator
from app.driver_assignment import AssignDriverRequest
from app.firestore_driver_assignment import DriverAssignmentConflict, DriverAssignmentMissing
from app.main import app, get_driver_assignment_repository
from app.optimized_routes import OptimizedRoute


class FakeRepository:
    outcome = None
    def assign(self, route_id, payload, *, operator_uid):
        assert operator_uid == "synthetic-operator"
        if self.outcome:
            raise self.outcome
        now = datetime.now(timezone.utc)
        return OptimizedRoute(
            id=route_id, driver_id=payload.driver_id,
            assigned_by=operator_uid, assigned_at=now,
            created_by=operator_uid,
            depot={"latitude": -12.095, "longitude": -77.035},
            order_ids=["o1"], baseline_order_ids=["o1"], ordered_order_ids=["o1"],
            baseline_seconds=300, optimized_seconds=270,
            baseline_meters=4500, optimized_meters=4300,
            improvement_pct=10, matrix_fingerprint="a"*64,
            version=payload.expected_version+1, created_at=now, updated_at=now,
        )


def _request():
    return {"driver_id": "synthetic-driver", "expected_version": 1,
            "idempotency_key": str(uuid4())}


def test_operator_can_assign_and_preserve_planned_status():
    fake = FakeRepository()
    app.dependency_overrides[require_operator] = lambda: UserContext(
        uid="synthetic-operator", role="OPERATOR")
    app.dependency_overrides[get_driver_assignment_repository] = lambda: fake
    try:
        route_id = str(uuid4())
        response = TestClient(app).post(
            f"/api/v1/optimized-routes/{route_id}/assign-driver",
            json=_request(),
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["driver_id"] == "synthetic-driver"
        assert body["status"] == "PLANNED"
        assert body["version"] == 2
        assert body["optimized_meters"] == 4300
    finally:
        app.dependency_overrides.clear()


def test_endpoint_rejects_unauthenticated_and_invalid_payload():
    url = f"/api/v1/optimized-routes/{uuid4()}/assign-driver"
    with TestClient(app) as client:
        assert client.post(url, json=_request()).status_code == 401
    app.dependency_overrides[require_operator] = lambda: UserContext(
        uid="synthetic-operator", role="OPERATOR")
    app.dependency_overrides[get_driver_assignment_repository] = FakeRepository
    try:
        data = _request()
        data["expected_version"] = 0
        assert TestClient(app).post(url, json=data).status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_endpoint_maps_storage_errors():
    fake = FakeRepository()
    url = f"/api/v1/optimized-routes/{uuid4()}/assign-driver"
    app.dependency_overrides[require_operator] = lambda: UserContext(
        uid="synthetic-operator", role="OPERATOR")
    app.dependency_overrides[get_driver_assignment_repository] = lambda: fake
    try:
        for error, code in [(DriverAssignmentMissing("missing"),404),
                            (DriverAssignmentConflict("busy"),409),
                            (RuntimeError("unavailable"),503)]:
            fake.outcome = error
            result = TestClient(app).post(url, json=_request())
            assert result.status_code == code, result.text
    finally:
        app.dependency_overrides.clear()


def test_driver_role_cannot_assign():
    def deny():
        raise HTTPException(status_code=403, detail="Operator role required")
    app.dependency_overrides[require_operator] = deny
    try:
        assert TestClient(app).post(
            f"/api/v1/optimized-routes/{uuid4()}/assign-driver",
            json=_request()).status_code == 403
    finally:
        app.dependency_overrides.clear()
