"""US-016 security contract tests, entirely in-memory, no GCP calls."""
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.auth import UserContext, require_operator
from app.main import app, get_public_tracking_repository
from app.public_tracking import (
    FirestorePublicTrackingRepository, LinkUnavailable, TrackingDisabled,
)

class Snapshot:
    def __init__(self, data):
        self.exists = data is not None
        self.data = data
    def to_dict(self):
        return self.data

class Doc:
    def __init__(self, bucket, key):
        self.bucket, self.key = bucket, key
    def get(self):
        return Snapshot(self.bucket.get(self.key))
    def create(self, data):
        assert self.key not in self.bucket
        self.bucket[self.key] = dict(data)
    def update(self, data):
        assert self.key in self.bucket
        self.bucket[self.key].update(data)

class Collection:
    def __init__(self, bucket):
        self.bucket = bucket
    def document(self, key):
        return Doc(self.bucket, key)

class DB:
    def __init__(self):
        self.data = {}
    def collection(self, name):
        return Collection(self.data.setdefault(name, {}))

def setup():
    db = DB()
    a, b = str(uuid4()), str(uuid4())
    for order_id, status in [(a, "IN_TRANSIT"), (b, "FAILED")]:
        db.collection("orders").document(order_id).create({
            "id": order_id, "status": status, "data_origin": "synthetic",
            "address_label": "Private destination", "geo": {"latitude": -12.1, "longitude": -77.1},
            "driver_id": "private-driver",
        })
    return FirestorePublicTrackingRepository(db), db, a, b

def test_disabled_by_default_fails_closed():
    repo, _, a, _ = setup()
    with patch.dict(os.environ, {}, clear=True):
        try:
            repo.issue(a)
            assert False, "Expected disabled feature"
        except TrackingDisabled:
            pass
        with TestClient(app) as client:
            response = client.post("/api/v1/public/tracking", json={"token": "x"*43})
            assert response.status_code == 404

def test_token_is_hashed_scoped_to_exactly_one_order_and_no_gps_leaks():
    repo, db, a, b = setup()
    with patch.dict(os.environ, {"SMARTROUTE_PUBLIC_TRACKING_ENABLED":"true"}):
        issued = repo.issue(a)
        assert issued.token not in str(db.data)
        assert len(db.data["public_tracking_links"]) == 1
        view = repo.resolve(issued.token).model_dump()
        assert view == {"order_reference":a, "status":"IN_TRANSIT", "eta_minutes":None}
        assert b not in str(view)
        for forbidden in ("geo", "driver", "latitude", "route_id", "address_label"):
            assert forbidden not in view
        other = repo.issue(b)
        assert repo.resolve(other.token).order_reference == b
        assert repo.resolve(issued.token).order_reference == a

def test_invalid_revoked_and_expired_tokens_denied():
    repo, db, a, _ = setup()
    with patch.dict(os.environ, {"SMARTROUTE_PUBLIC_TRACKING_ENABLED":"true"}):
        token = repo.issue(a).token
        for bad in ("a", "../"+token, "z"*43):
            try:
                repo.resolve(bad)
                assert False, "Expected unavailable"
            except LinkUnavailable:
                pass
        repo.revoke(token)
        try:
            repo.resolve(token)
            assert False
        except LinkUnavailable:
            pass
        next_token = repo.issue(a).token
        key = next(iter(k for k, value in db.data["public_tracking_links"].items() if not value["revoked"]))
        db.data["public_tracking_links"][key]["expires_at"] = datetime.now(timezone.utc)-timedelta(seconds=1)
        try:
            repo.resolve(next_token)
            assert False
        except LinkUnavailable:
            pass

def test_public_endpoint_does_not_require_login_but_operator_issuance_does():
    repo, _, a, _ = setup()
    app.dependency_overrides[get_public_tracking_repository] = lambda: repo
    try:
        with patch.dict(os.environ, {"SMARTROUTE_PUBLIC_TRACKING_ENABLED":"true"}):
            with TestClient(app) as client:
                assert client.post(f"/api/v1/orders/{a}/tracking-link").status_code == 401
                app.dependency_overrides[require_operator] = lambda: UserContext(uid="synthetic-operator",role="OPERATOR")
                issued = client.post(f"/api/v1/orders/{a}/tracking-link")
                assert issued.status_code == 200, issued.text
                token = issued.json()["token"]
                app.dependency_overrides.pop(require_operator)
                res = client.post("/api/v1/public/tracking",json={"token":token})
                assert res.status_code == 200
                assert res.json()["order_reference"] == a
                assert res.headers["cache-control"] == "no-store"
                assert res.headers["x-robots-tag"] == "noindex, nofollow"
                assert client.get("/api/v1/orders").status_code == 401
                assert client.post("/api/v1/public/tracking",json={"token":"z"*43}).status_code == 404
    finally:
        app.dependency_overrides.clear()

def test_nonsynthetic_order_cannot_get_public_link():
    repo, db, a, _ = setup()
    db.data["orders"][a]["data_origin"] = "observed"
    with patch.dict(os.environ, {"SMARTROUTE_PUBLIC_TRACKING_ENABLED":"true"}):
        try:
            repo.issue(a)
            assert False
        except LinkUnavailable:
            pass
