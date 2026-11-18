"""US-010 API contract tests; no GCP or ORS calls."""
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.auth import UserContext, require_operator
from app.main import app, get_optimized_route_repository
from app.optimized_routes import OptimizedRoute, OptimizedRouteConflict, OptimizedRouteMissing


def operator():
    return UserContext(uid="synthetic-operator", role="OPERATOR")


def example_route(order_ids, route_id=None):
    now = datetime.now(timezone.utc)
    return OptimizedRoute(
        id=route_id or str(uuid4()), created_by="synthetic-operator",
        depot={"latitude": -12.095, "longitude": -77.035},
        order_ids=order_ids, baseline_order_ids=order_ids,
        ordered_order_ids=list(reversed(order_ids)),
        baseline_seconds=300, optimized_seconds=270,
        baseline_meters=4500, optimized_meters=4300,
        improvement_pct=10.0, matrix_fingerprint="a" * 64,
        created_at=now, updated_at=now,
    )


class FakeOptimizedRoutes:
    def __init__(self):
        self.saved = {}
        self.keys = {}

    def save(self, payload, *, actor_uid):
        key = str(payload.idempotency_key)
        value = (payload.order_ids, payload.depot.model_dump())
        if key in self.keys:
            if self.keys[key][0] != value:
                raise OptimizedRouteConflict("Key reused")
            return self.keys[key][1], False
        route = example_route(payload.order_ids)
        self.keys[key] = (value, route)
        self.saved[route.id] = route
        return route, True

    def get(self, route_id):
        if route_id not in self.saved:
            raise OptimizedRouteMissing("Route not found")
        return self.saved[route_id]

    def detail(self, route_id):
        from app.optimized_routes import OptimizedRouteDetail
        return OptimizedRouteDetail(**self.get(route_id).model_dump(mode="python"))

    def list(self, *, limit, after):
        from app.optimized_routes import OptimizedRoutePage
        return OptimizedRoutePage(items=list(self.saved.values())[:limit])


def payload(key=None):
    return {"depot": {"latitude": -12.095, "longitude": -77.035},
            "order_ids": ["o1", "o2"], "idempotency_key": key or str(uuid4())}


def test_save_get_list_and_idempotent_retry():
    fake = FakeOptimizedRoutes()
    app.dependency_overrides[require_operator] = operator
    app.dependency_overrides[get_optimized_route_repository] = lambda: fake
    try:
        with TestClient(app) as client:
            data = payload()
            first = client.post("/api/v1/optimized-routes", json=data)
            assert first.status_code == 201, first.text
            route_id = first.json()["id"]
            assert first.json()["status"] == "PLANNED"
            assert first.json()["driver_id"] is None
            assert first.json()["data_origin"] == "estimated"
            retry = client.post("/api/v1/optimized-routes", json=data)
            assert retry.status_code == 200 and retry.json()["id"] == route_id
            detail = client.get(f"/api/v1/optimized-routes/{route_id}")
            assert detail.status_code == 200
            assert detail.json()["ordered_order_ids"] == ["o2", "o1"]
            listed = client.get("/api/v1/optimized-routes?limit=10")
            assert listed.status_code == 200 and len(listed.json()["items"]) == 1
            data["order_ids"] = ["o3"]
            assert client.post("/api/v1/optimized-routes", json=data).status_code == 409
            assert client.get("/api/v1/optimized-routes/missing").status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_invalid_requests_cannot_write():
    fake = FakeOptimizedRoutes()
    app.dependency_overrides[require_operator] = operator
    app.dependency_overrides[get_optimized_route_repository] = lambda: fake
    try:
        with TestClient(app) as client:
            bad = payload()
            bad["order_ids"] = ["o1", "o1"]
            assert client.post("/api/v1/optimized-routes", json=bad).status_code == 422
            bad = payload()
            bad["depot"]["latitude"] = -100
            assert client.post("/api/v1/optimized-routes", json=bad).status_code == 422
            bad = payload()
            bad["order_ids"] = []
            assert client.post("/api/v1/optimized-routes", json=bad).status_code == 422
            assert client.get("/api/v1/optimized-routes?limit=51").status_code == 422
            assert not fake.saved
    finally:
        app.dependency_overrides.clear()


def test_authorization_required_for_all_endpoints():
    with TestClient(app) as client:
        assert client.post("/api/v1/optimized-routes", json=payload()).status_code == 401
        assert client.get("/api/v1/optimized-routes").status_code == 401
        assert client.get("/api/v1/optimized-routes/test").status_code == 401

    def driver():
        raise HTTPException(403, "Operator role required")

    app.dependency_overrides[require_operator] = driver
    try:
        with TestClient(app) as client:
            assert client.post("/api/v1/optimized-routes", json=payload()).status_code == 403
            assert client.get("/api/v1/optimized-routes").status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_active_route_is_readable_by_operator_after_driver_start():
    from app.optimized_routes import OptimizedRoutePage, OptimizedRouteDetail
    route = example_route(["o1", "o2"])
    active = route.model_dump(mode="python")
    active["status"] = "ACTIVE"
    active["driver_id"] = "synthetic-driver"
    active["started_by"] = "synthetic-driver"
    active["started_at"] = datetime.now(timezone.utc)
    listed = OptimizedRoutePage(items=[active])
    assert listed.items[0].status == "ACTIVE"
    assert listed.items[0].started_at == active["started_at"]
    detailed = OptimizedRouteDetail(**active)
    assert detailed.status == "ACTIVE"
    assert detailed.started_by == "synthetic-driver"
