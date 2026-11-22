"""US-008: contract and freshness regression (no live GCP)."""
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.auth import UserContext, require_driver, require_operator
from app.main import app, get_driver_location_repository
from app.driver_location import GPSFix, GPSDenied, GPSMissing, freshness

NOW=datetime.now(timezone.utc)
FIX={
    "route_id":"synthetic-route",
    "latitude":-12.095,"longitude":-77.035,"accuracy_m":15.0,
    "captured_at":NOW.isoformat(),"consent":True,
}

class FakeLocation:
    def __init__(self):
        self.last=None
        self.active=True
    def record(self, *, driver_uid, fix):
        if not self.active:raise GPSDenied("GPS only permitted on ACTIVE route")
        self.last=(driver_uid,fix)
        return {"route_id":fix.route_id,"stored_at":datetime.now(timezone.utc),"status":"CURRENT"}
    def latest(self, *, route_id):
        if self.last is None:raise GPSMissing("No GPS")
        uid,fix=self.last
        return {"route_id":route_id,"driver_id":uid,
                "latitude":fix.latitude,"longitude":fix.longitude,
                "accuracy_m":fix.accuracy_m,
                "captured_at":fix.captured_at,
                "stored_at":datetime.now(timezone.utc),"status":"CURRENT"}

def test_no_consent_and_old_timestamp_cannot_be_persisted():
    for changes in (
        {"consent":False}, {"captured_at":(NOW-timedelta(minutes=4)).isoformat()},
        {"latitude":-13.0},{"accuracy_m":1000},
        {"captured_at":NOW.replace(tzinfo=None).isoformat()},
    ):
        try:
            GPSFix.model_validate({**FIX,**changes})
            assert False,"Invalid fix was accepted"
        except ValidationError:
            pass

def test_stale_threshold_exactly_120_seconds():
    t=datetime(2026,11,22,15,0,tzinfo=timezone.utc)
    assert freshness(t, t+timedelta(seconds=120))=="CURRENT"
    assert freshness(t, t+timedelta(seconds=121))=="STALE"

def test_driver_post_and_operator_get_use_verified_identity():
    repo=FakeLocation()
    app.dependency_overrides[require_driver]=lambda:UserContext(uid="driver-qa",role="DRIVER")
    app.dependency_overrides[require_operator]=lambda:UserContext(uid="operator-qa",role="OPERATOR")
    app.dependency_overrides[get_driver_location_repository]=lambda:repo
    try:
        api=TestClient(app)
        posted=api.post("/api/v1/driver/me/location",json=FIX)
        assert posted.status_code==200,posted.text
        assert repo.last[0]=="driver-qa"
        got=api.get("/api/v1/routes/synthetic-route/location")
        assert got.status_code==200 and got.json()["driver_id"]=="driver-qa"
        repo.active=False
        assert api.post("/api/v1/driver/me/location",json=FIX).status_code==403
    finally:app.dependency_overrides.clear()

def test_anonymous_and_wrong_role_gps_denied():
    api=TestClient(app)
    assert api.post("/api/v1/driver/me/location",json=FIX).status_code==401
    assert api.get("/api/v1/routes/synthetic-route/location").status_code==401
    app.dependency_overrides[require_driver]=lambda:(_ for _ in ()).throw(HTTPException(403,"DRIVER required"))
    try:assert TestClient(app).post("/api/v1/driver/me/location",json=FIX).status_code==403
    finally:app.dependency_overrides.clear()
