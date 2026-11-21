"""US-012/013/014 transactional E2E on Firestore emulator ONLY; never live GCP."""
import os
from uuid import uuid4
from datetime import datetime, timezone

import pytest

from app.driver_workflow import WorkflowRequest, StopResultRequest
from app.firestore_driver_workflow import (
    FirestoreDriverWorkflowRepository, WorkflowConflict,
)
from app.qa_write_guard import QaWriteGuardDenied
from app.firestore_driver_assignment import FirestoreDriverAssignmentRepository


@pytest.mark.skipif(
    not os.getenv("FIRESTORE_EMULATOR_HOST"),
    reason="Requires Firestore emulator; never runs against live Firestore",
)
def test_driver_start_deliver_fail_complete_idempotency_and_ownership(monkeypatch):
    from google.cloud import firestore

    from app.orders import OrderCreate, new_order
    from app.optimized_routes import OptimizedRoute
    db = firestore.Client(project="demo-smartroute")
    suffix = uuid4().hex[:12]
    uid = "synthetic-driver-" + suffix
    route_id = "synthetic-route-" + suffix
    order_ids = ["synthetic-order-" + suffix + "-1", "synthetic-order-" + suffix + "-2"]
    db.collection("users").document(uid).create({"uid": uid, "active": True, "role": "DRIVER"})
    db.collection("drivers").document(uid).create({
        "uid": uid, "active": True, "available": True, "display_name": "Emulator QA",
    })
    now = datetime.now(timezone.utc)
    route = OptimizedRoute(
        id=route_id, created_by="synthetic-operator", driver_id=uid,
        assigned_by="synthetic-operator", assigned_at=now,
        status="PLANNED", version=2,
        depot={"latitude": -12.095, "longitude": -77.035},
        order_ids=order_ids, baseline_order_ids=order_ids,
        ordered_order_ids=order_ids,
        baseline_seconds=650, optimized_seconds=600,
        baseline_meters=2800, optimized_meters=2500,
        improvement_pct=10.0, matrix_fingerprint="a" * 64,
        created_at=now, updated_at=now,
    )
    db.collection("routes").document(route_id).create({
        **route.model_dump(mode="python"),
        "stop_snapshots": [{
            "id": oid, "address_label": "Synthetic stop",
            "geo": {"latitude": -12.1, "longitude": -77.04},
        } for oid in order_ids],
    })
    for oid in order_ids:
        order = new_order(OrderCreate(
            address_label="Synthetic stop",
            geo={"latitude": -12.1, "longitude": -77.04},
        ), actor_uid="synthetic-operator")
        db.collection("orders").document(oid).create({
            **order.model_dump(mode="python"),
            "id": oid, "route_id": route_id, "status": "ASSIGNED",
            "version": 2,
        })
    db.collection("driver_assignments").document(uid).create({
        "driver_id": uid, "route_id": route_id, "status": "RESERVED", "version": 1,
    })

    workflow = FirestoreDriverWorkflowRepository(db)
    projection = FirestoreDriverAssignmentRepository(db)
    monkeypatch.setenv("SMARTROUTE_QA_WRITE_GUARD", "true")
    monkeypatch.setenv("SMARTROUTE_QA_DRIVER_UID", "other-qa-driver")
    monkeypatch.setenv("SMARTROUTE_QA_ROUTE_ID", "other-qa-route")
    with pytest.raises(QaWriteGuardDenied):
        workflow.execute(driver_uid=uid, action="start",
                         payload=WorkflowRequest(expected_version=2, idempotency_key=uuid4()))
    assert db.collection("routes").document(route_id).get().to_dict()["status"] == "PLANNED"
    assert db.collection("driver_assignments").document(uid).get().to_dict()["status"] == "RESERVED"
    assert all(db.collection("orders").document(oid).get().to_dict()["status"] == "ASSIGNED"
               for oid in order_ids)
    monkeypatch.setenv("SMARTROUTE_QA_DRIVER_UID", uid)
    monkeypatch.setenv("SMARTROUTE_QA_ROUTE_ID", route_id)
    start = WorkflowRequest(expected_version=2, idempotency_key=uuid4())
    receipt = workflow.execute(driver_uid=uid, action="start", payload=start)
    assert receipt == {"id": route_id, "status": "ACTIVE", "version": 3}
    assert workflow.execute(driver_uid=uid, action="start", payload=start) == receipt
    assert db.collection("routes").document(route_id).get().to_dict()["version"] == 3
    assert db.collection("driver_assignments").document(uid).get().to_dict()["status"] == "ACTIVE"
    assert [s.status for s in projection.own_route(driver_uid=uid).stops] == [
        "IN_TRANSIT", "IN_TRANSIT",
    ]

    with pytest.raises(WorkflowConflict):
        workflow.execute(
            driver_uid=uid, action="deliver",
            order_id=order_ids[0],
            payload=StopResultRequest(expected_version=2, idempotency_key=uuid4()),
        )
    with pytest.raises(WorkflowConflict):
        workflow.execute(
            driver_uid=uid, action="deliver",
            order_id=order_ids[0],
            payload=StopResultRequest(expected_version=3, idempotency_key=start.idempotency_key),
        )

    deliver = StopResultRequest(expected_version=3, idempotency_key=uuid4())
    d = workflow.execute(driver_uid=uid, action="deliver", payload=deliver, order_id=order_ids[0])
    assert d["order_status"] == "DELIVERED" and d["version"] == 4
    assert workflow.execute(driver_uid=uid, action="deliver", payload=deliver, order_id=order_ids[0]) == d
    with pytest.raises(WorkflowConflict):
        workflow.execute(
            driver_uid=uid, action="complete",
            payload=WorkflowRequest(expected_version=4, idempotency_key=uuid4()),
        )
    fail = StopResultRequest(expected_version=4, idempotency_key=uuid4(), reason="Local cerrado")
    f = workflow.execute(driver_uid=uid, action="fail", payload=fail, order_id=order_ids[1])
    assert f["order_status"] == "FAILED" and f["version"] == 5
    assert [s.status for s in projection.own_route(driver_uid=uid).stops] == ["DELIVERED", "FAILED"]

    complete = WorkflowRequest(expected_version=5, idempotency_key=uuid4())
    done = workflow.execute(driver_uid=uid, action="complete", payload=complete)
    assert done == {"id": route_id, "status": "COMPLETED", "version": 6}
    assert workflow.execute(driver_uid=uid, action="complete", payload=complete) == done
    assert not db.collection("driver_assignments").document(uid).get().exists
    assert db.collection("drivers").document(uid).get().to_dict()["available"] is True
    final = projection.own_route(driver_uid=uid)
    assert final.status == "COMPLETED" and final.version == 6
    assert [s.status for s in final.stops] == ["DELIVERED", "FAILED"]
    assert db.collection("routes").document(route_id).get().to_dict()["completed_summary"] == {
        "delivered": 1, "failed": 1, "total": 2,
    }
    events = list(db.collection("driver_route_events").where("route_id", "==", route_id).stream())
    assert len(events) == 4


def test_emulator_is_required_for_workflow_integration():
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        pytest.skip("Emulator available")
    if os.getenv("FIRESTORE_EMULATOR_REQUIRED") == "1":
        pytest.fail("FIRESTORE_EMULATOR_HOST is required; refusing live Firestore")
