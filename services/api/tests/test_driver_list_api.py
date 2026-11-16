"""US-011 driver candidate API tests; no cloud or Firestore access."""
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.auth import UserContext, require_operator
from app.driver_assignment import DriverPage, DriverSummary
from app.main import app, get_driver_assignment_repository


class FakeDrivers:
    def list_available(self, *, limit, after):
        assert limit == 20
        assert after is None
        return DriverPage(items=[
            DriverSummary(uid="synthetic-driver-1",
                          display_name="Conductor piloto", active=True, available=True)
        ])


def test_operator_can_list_available_driver_candidates():
    app.dependency_overrides[require_operator] = lambda: UserContext(
        uid="synthetic-operator", role="OPERATOR")
    app.dependency_overrides[get_driver_assignment_repository] = FakeDrivers
    try:
        resp = TestClient(app).get("/api/v1/drivers?available=true")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["items"][0]["uid"] == "synthetic-driver-1"
        assert "email" not in data["items"][0]
    finally:
        app.dependency_overrides.clear()


def test_candidates_require_auth_and_operator_role():
    assert TestClient(app).get("/api/v1/drivers").status_code == 401
    def deny():
        raise HTTPException(403, "Operator role required")
    app.dependency_overrides[require_operator] = deny
    try:
        assert TestClient(app).get("/api/v1/drivers").status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_invalid_listing_requests_rejected():
    app.dependency_overrides[require_operator] = lambda: UserContext(
        uid="synthetic-operator", role="OPERATOR")
    app.dependency_overrides[get_driver_assignment_repository] = FakeDrivers
    try:
        c = TestClient(app)
        assert c.get("/api/v1/drivers?limit=21").status_code == 422
        assert c.get("/api/v1/drivers?available=false").status_code == 422
    finally:
        app.dependency_overrides.clear()
