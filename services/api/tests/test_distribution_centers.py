"""US-017 API contract tests (in-memory repository, no GCP writes)."""
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.auth import UserContext, require_operator
from app.main import app, get_center_repository
from app.distribution_centers import (
    CenterCreate, CenterUpdate, CenterNotFound, CenterConflict,
    CenterPage, create_center,
)

class MemoryCenterRepository:
    def __init__(self):
        self.items = {}
        self.codes = set()
    def create(self, payload, *, actor_uid):
        c = create_center(payload, actor_uid)
        if c.code in self.codes: raise CenterConflict("Duplicado")
        self.codes.add(c.code)
        self.items[c.id] = c
        return c
    def get(self, center_id):
        if center_id not in self.items: raise CenterNotFound("No existe")
        return self.items[center_id]
    def list(self, *, limit, after):
        ids = sorted(self.items)
        if after:
            if after not in self.items: raise ValueError("cursor")
            ids = [x for x in ids if x > after]
        return CenterPage(items=[self.items[x] for x in ids[:limit]],
                          next_cursor=ids[limit-1] if len(ids)>limit else None)
    def update(self, center_id, payload):
        old = self.get(center_id)
        if not old.active or old.version != payload.expected_version or old.code != payload.code.upper():
            raise CenterConflict("Conflicto")
        payload.ensure_valid()
        updated=old.model_copy(update={
            "name":payload.name,"address_label":payload.address_label,
            "geo":payload.geo,"location_precision":payload.location_precision,
            "version":old.version+1,
        })
        self.items[center_id]=updated
        return updated
    def deactivate(self, center_id, *, expected_version):
        old=self.get(center_id)
        if not old.active or old.version!=expected_version:raise CenterConflict("Conflicto")
        updated=old.model_copy(update={"active":False,"version":old.version+1})
        self.items[center_id]=updated
        return updated

def operator(): return UserContext(uid="qa-operator",role="OPERATOR")

PAYLOAD={
    "code":"CD-LIMA-01","name":"Centro Lima QA",
    "address_label":"Calle sintética 123, Lima",
    "geo":{"latitude":-12.095,"longitude":-77.035},
    "location_precision":"approximate", "approximate_confirmed":True,
}

def test_centers_crud_create_read_update_deactivate_and_preserve_history():
    repo=MemoryCenterRepository()
    app.dependency_overrides[require_operator]=operator
    app.dependency_overrides[get_center_repository]=lambda:repo
    try:
        with TestClient(app) as api:
            created=api.post("/api/v1/distribution-centers",json=PAYLOAD)
            assert created.status_code==201,created.text
            c=created.json()
            assert c["code"]=="CD-LIMA-01" and c["active"] is True
            assert api.get("/api/v1/distribution-centers").json()["items"][0]["id"]==c["id"]
            assert api.get("/api/v1/distribution-centers/"+c["id"]).status_code==200
            assert api.post("/api/v1/distribution-centers",json=PAYLOAD).status_code==409
            update={**PAYLOAD,"name":"Centro Lima Actualizado","expected_version":1}
            changed=api.put("/api/v1/distribution-centers/"+c["id"],json=update)
            assert changed.status_code==200 and changed.json()["version"]==2
            assert api.put("/api/v1/distribution-centers/"+c["id"],json=update).status_code==409
            assert api.delete("/api/v1/distribution-centers/"+c["id"],json={"expected_version":1}).status_code==409
            disabled=api.request("DELETE","/api/v1/distribution-centers/"+c["id"],json={"expected_version":2})
            assert disabled.status_code==200 and disabled.json()["active"] is False
            assert api.get("/api/v1/distribution-centers/"+c["id"]).json()["name"]=="Centro Lima Actualizado"
            assert api.put("/api/v1/distribution-centers/"+c["id"],json={**update,"expected_version":3}).status_code==409
    finally:app.dependency_overrides.clear()

def test_centers_validation_rejects_unconfirmed_or_outside_lima():
    app.dependency_overrides[require_operator]=operator
    app.dependency_overrides[get_center_repository]=MemoryCenterRepository
    try:
        with TestClient(app) as api:
            assert api.post("/api/v1/distribution-centers",json={**PAYLOAD,"approximate_confirmed":False}).status_code==422
            assert api.post("/api/v1/distribution-centers",json={**PAYLOAD,"geo":{"latitude":-10.0,"longitude":-77.0}}).status_code==422
            assert api.post("/api/v1/distribution-centers",json={**PAYLOAD,"code":"invalid/path"}).status_code==422
            assert api.get("/api/v1/distribution-centers?limit=51").status_code==422
            assert api.get("/api/v1/distribution-centers/no-such-id").status_code==404
    finally:app.dependency_overrides.clear()

def test_centers_require_operator():
    with TestClient(app) as api:
        assert api.get("/api/v1/distribution-centers").status_code==401
        assert api.post("/api/v1/distribution-centers",json=PAYLOAD).status_code==401
    def reject():raise HTTPException(status_code=403,detail="Operator required")
    app.dependency_overrides[require_operator]=reject
    try:
        with TestClient(app) as api:
            assert api.get("/api/v1/distribution-centers").status_code==403
            assert api.post("/api/v1/distribution-centers",json=PAYLOAD).status_code==403
    finally:app.dependency_overrides.clear()
