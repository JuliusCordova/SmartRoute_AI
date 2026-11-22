"""US-V1-008: Firestore emulator only. AC-006 deny GPS outside ACTIVE, AC-007 STALE."""
import os
from datetime import datetime, timezone, timedelta
from uuid import uuid4
import pytest
from app.driver_location import GPSFix, GPSDenied, GPSMissing
from app.firestore_driver_location import FirestoreDriverLocationRepository
from app.firestore_driver_workflow import FirestoreDriverWorkflowRepository
from app.driver_workflow import WorkflowRequest

@pytest.mark.skipif(not os.getenv("FIRESTORE_EMULATOR_HOST"),reason="Firestore emulator required")
def test_gps_active_owned_stale_and_completion_cleanup(monkeypatch):
    from google.cloud import firestore
    db=firestore.Client(project="demo-smartroute")
    suffix=uuid4().hex[:12]
    uid="synthetic-driver-"+suffix
    rid="synthetic-route-"+suffix
    oid="synthetic-order-"+suffix
    now=datetime.now(timezone.utc)
    db.collection("users").document(uid).create({"role":"DRIVER","active":True})
    db.collection("drivers").document(uid).create({"uid":uid,"active":True,"available":False})
    db.collection("routes").document(rid).create({
        "id":rid,"route_type":"OPTIMIZED","status":"PLANNED","driver_id":uid,
        "version":2,"ordered_order_ids":[oid],
    })
    db.collection("orders").document(oid).create({
        "id":oid,"route_id":rid,"status":"ASSIGNED","version":1,
    })
    db.collection("driver_assignments").document(uid).create({
        "driver_id":uid,"route_id":rid,"status":"RESERVED","version":1,
    })
    monkeypatch.setenv("SMARTROUTE_QA_WRITE_GUARD","true")
    monkeypatch.setenv("SMARTROUTE_QA_DRIVER_UID",uid)
    monkeypatch.setenv("SMARTROUTE_QA_ROUTE_ID",rid)
    location=FirestoreDriverLocationRepository(db)
    workflow=FirestoreDriverWorkflowRepository(db)
    fix=GPSFix(route_id=rid,latitude=-12.095,longitude=-77.035,
               accuracy_m=12,captured_at=now,consent=True)
    ref=db.collection("driver_last_locations").document(rid)
    # AC-006: PLANNED reject with zero writes
    with pytest.raises(GPSDenied):
        location.record(driver_uid=uid,fix=fix)
    assert not ref.get().exists
    workflow.execute(driver_uid=uid,action="start",
        payload=WorkflowRequest(expected_version=2,idempotency_key=uuid4()))
    with pytest.raises(GPSDenied):
        location.record(driver_uid="other-driver",fix=fix)
    assert not ref.get().exists
    saved=location.record(driver_uid=uid,fix=fix)
    assert saved.status=="CURRENT"
    got=location.latest(route_id=rid)
    assert got.status=="CURRENT" and got.driver_id==uid
    # AC-007: position older than 120 seconds is stale, never shown as current
    ref.update({"stored_at":datetime.now(timezone.utc)-timedelta(seconds=125)})
    assert location.latest(route_id=rid).status=="STALE"
    # Simulate completion of the sole test delivery; workflow cleans location atomically.
    db.collection("orders").document(oid).update({"status":"DELIVERED"})
    workflow.execute(driver_uid=uid,action="complete",
        payload=WorkflowRequest(expected_version=3,idempotency_key=uuid4()))
    assert not ref.get().exists
    with pytest.raises(GPSDenied):
        location.record(driver_uid=uid,fix=fix)
    with pytest.raises(GPSMissing):
        location.latest(route_id=rid)
