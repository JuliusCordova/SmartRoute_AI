"""US-005 API guards without accessing billed GCP services."""
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.auth import UserContext, require_operator
from app.main import app, get_route_repository
from app.routes import RecordMissing, AssignmentConflict

class FakeRoutes:
    def __init__(self):
        self.created = []
        self.assignments = []
    def create(self, route):
        self.created.append(route)
    def assign(self, route_id, order_ids):
        self.assignments.append((route_id, order_ids))
        if route_id == "missing":
            raise RecordMissing("Route not found")
        if route_id == "conflict":
            raise AssignmentConflict("Order already assigned")
        return {"route_id": route_id, "order_ids": order_ids, "assigned": len(order_ids)}

def operator(): return UserContext(uid="synthetic-operator", role="OPERATOR")

def test_create_and_assign_route():
    fake=FakeRoutes()
    app.dependency_overrides[require_operator]=operator
    app.dependency_overrides[get_route_repository]=lambda: fake
    try:
        with TestClient(app) as api:
            r=api.post("/api/v1/routes",json={"driver_id":"synthetic-driver","depot":{"latitude":-12.08,"longitude":-77.01}})
            assert r.status_code==201, r.text
            assert r.json()["status"]=="DRAFT"
            route_id=r.json()["id"]
            a=api.post(f"/api/v1/routes/{route_id}/orders",json={"order_ids":["synthetic-order-1"]})
            assert a.status_code==200
            assert a.json()["assigned"]==1
    finally: app.dependency_overrides.clear()

def test_invalid_capacity_and_coordinates():
    fake=FakeRoutes()
    app.dependency_overrides[require_operator]=operator
    app.dependency_overrides[get_route_repository]=lambda: fake
    try:
        with TestClient(app) as api:
            assert api.post("/api/v1/routes",json={"driver_id":"x","depot":{"latitude":999,"longitude":0}}).status_code==422
            assert api.post("/api/v1/routes/r/orders",json={"order_ids":[]}).status_code==422
            assert api.post("/api/v1/routes/r/orders",json={"order_ids":["x"]*11}).status_code==422
            assert not fake.created and not fake.assignments
    finally: app.dependency_overrides.clear()

def test_conflict_and_missing_are_mapped():
    app.dependency_overrides[require_operator]=operator
    app.dependency_overrides[get_route_repository]=FakeRoutes
    try:
        with TestClient(app) as api:
            assert api.post("/api/v1/routes/missing/orders",json={"order_ids":["o"]}).status_code==404
            assert api.post("/api/v1/routes/conflict/orders",json={"order_ids":["o"]}).status_code==409
    finally: app.dependency_overrides.clear()

def test_roles_enforced_without_store_access():
    with TestClient(app) as api:
        assert api.post("/api/v1/routes",json={"driver_id":"x","depot":{"latitude":0,"longitude":0}}).status_code==401
        assert api.post("/api/v1/routes/r/orders",json={"order_ids":["x"]}).status_code==401
    def driver(): raise HTTPException(status_code=403,detail="Operator role required")
    app.dependency_overrides[require_operator]=driver
    try:
        with TestClient(app) as api:
            assert api.post("/api/v1/routes",json={"driver_id":"x","depot":{"latitude":0,"longitude":0}}).status_code==403
    finally: app.dependency_overrides.clear()
