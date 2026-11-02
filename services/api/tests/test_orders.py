"""US-003/004 deterministic unit tests: no real GCP access."""
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.auth import UserContext, require_operator
from app.main import app, get_repository
from app.orders import OrderPage

class MemoryRepo:
    def __init__(self): self.orders = {}
    def create(self, order):
        assert order.id not in self.orders
        self.orders[order.id] = order
    def list(self, *, limit, after):
        ids = sorted(self.orders)
        if after is not None:
            if after not in ids: raise ValueError("bad cursor")
            ids = [i for i in ids if i > after]
        page = ids[:limit]
        return OrderPage(items=[self.orders[i] for i in page],
                         next_cursor=page[-1] if len(ids)>limit else None)

def operator_override(): return UserContext(uid="synthetic-operator", role="OPERATOR")

def test_create_and_list_synthetic_orders():
    repo = MemoryRepo()
    app.dependency_overrides[require_operator] = operator_override
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        with TestClient(app) as api:
            r = api.post("/api/v1/orders", json={"address_label":"Destino sintético 1","geo":{"latitude":-12.09,"longitude":-77.04}})
            assert r.status_code == 201, r.text
            body = r.json()
            assert body["status"] == "PENDING" and body["data_origin"] == "synthetic"
            assert body["created_by"] == "synthetic-operator"
            assert api.get("/api/v1/orders").json()["items"][0]["id"] == body["id"]
    finally: app.dependency_overrides.clear()

def test_invalid_coordinates_rejected_without_write():
    repo = MemoryRepo()
    app.dependency_overrides[require_operator] = operator_override
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        with TestClient(app) as api:
            for geo in [{"latitude": -91,"longitude":0},{"latitude":1,"longitude":181}]:
                assert api.post("/api/v1/orders",json={"address_label":"Destino sintético 1","geo":geo}).status_code == 422
            assert not repo.orders
    finally: app.dependency_overrides.clear()

def test_no_auth_is_401():
    with TestClient(app) as api:
        assert api.get("/api/v1/orders").status_code == 401
        assert api.post("/api/v1/orders",json={"address_label":"Destino sintético 1","geo":{"latitude":0,"longitude":0}}).status_code == 401

def test_driver_is_forbidden():
    def deny_driver(): raise HTTPException(status_code=403, detail="Operator role required")
    app.dependency_overrides[require_operator] = deny_driver
    try:
        with TestClient(app) as api:
            assert api.get("/api/v1/orders").status_code == 403
            assert api.post("/api/v1/orders",json={"address_label":"Destino sintético 1","geo":{"latitude":0,"longitude":0}}).status_code == 403
    finally: app.dependency_overrides.clear()

def test_limit_and_cursor_validation():
    app.dependency_overrides[require_operator] = operator_override
    app.dependency_overrides[get_repository] = MemoryRepo
    try:
        with TestClient(app) as api:
            assert api.get("/api/v1/orders?limit=51").status_code == 422
            assert api.get("/api/v1/orders?cursor=unknown").status_code == 422
    finally: app.dependency_overrides.clear()
