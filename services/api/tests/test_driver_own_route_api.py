"""US-011: driver can only fetch own route, never operator/global routes."""
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.auth import UserContext, require_driver
from app.driver_assignment import DriverRoute
from app.firestore_driver_assignment import DriverAssignmentConflict
from app.main import app, get_driver_assignment_repository


class FakeOwnRouteRepository:
    def __init__(self, assigned=True, failure=False):
        self.assigned = assigned
        self.failure = failure
        self.called_with = None

    def own_route(self, *, driver_uid):
        self.called_with = driver_uid
        if self.failure:
            raise DriverAssignmentConflict("invalid reservation")
        if not self.assigned:
            return None
        return DriverRoute(
            id=str(uuid4()), status="PLANNED", version=2,
            depot={"latitude": -12.095, "longitude": -77.035},
            stops=[{
                "sequence": 1, "order_id": "synthetic-order",
                "address_label": "Destino sintético Lima",
                "geo": {"latitude": -12.1, "longitude": -77.04},
            }],
            optimized_seconds=900, optimized_meters=5600,
            assigned_at=datetime.now(timezone.utc),
        )


def test_driver_reads_only_own_route():
    repo = FakeOwnRouteRepository()
    app.dependency_overrides[require_driver] = lambda: UserContext(
        uid="synthetic-driver-own", role="DRIVER")
    app.dependency_overrides[get_driver_assignment_repository] = lambda: repo
    try:
        response = TestClient(app).get("/api/v1/driver/me/route")
        assert response.status_code == 200, response.text
        assert repo.called_with == "synthetic-driver-own"
        data = response.json()
        assert data["stops"][0]["address_label"] == "Destino sintético Lima"
        assert data["data_origin"] == "estimated"
        assert data["version"] == 2
        assert "driver_id" not in data
        assert "created_by" not in data
        assert "route_geometry" not in data
    finally:
        app.dependency_overrides.clear()


def test_no_route_yields_http_204():
    repo = FakeOwnRouteRepository(assigned=False)
    app.dependency_overrides[require_driver] = lambda: UserContext(
        uid="synthetic-driver-empty", role="DRIVER")
    app.dependency_overrides[get_driver_assignment_repository] = lambda: repo
    try:
        response = TestClient(app).get("/api/v1/driver/me/route")
        assert response.status_code == 204 and response.content == b""
    finally:
        app.dependency_overrides.clear()


def test_missing_token_denied():
    assert TestClient(app).get("/api/v1/driver/me/route").status_code == 401


def test_operator_role_denied_to_driver_endpoint():
    def deny_operator():
        raise HTTPException(403, "Driver role required")
    app.dependency_overrides[require_driver] = deny_operator
    try:
        assert TestClient(app).get("/api/v1/driver/me/route").status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_inconsistent_own_reservation_fails_closed():
    repo = FakeOwnRouteRepository(failure=True)
    app.dependency_overrides[require_driver] = lambda: UserContext(
        uid="synthetic-driver-own", role="DRIVER")
    app.dependency_overrides[get_driver_assignment_repository] = lambda: repo
    try:
        assert TestClient(app).get("/api/v1/driver/me/route").status_code == 409
    finally:
        app.dependency_overrides.clear()
