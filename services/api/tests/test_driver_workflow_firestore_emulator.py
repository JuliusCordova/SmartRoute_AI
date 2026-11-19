"""US-012/013/014 transactional E2E on Firestore emulator ONLY; never live GCP."""
import os
from uuid import uuid4

import pytest

from app.driver_workflow import WorkflowRequest, StopResultRequest
from app.firestore_driver_workflow import (
    FirestoreDriverWorkflowRepository, WorkflowConflict,
)
from app.firestore_driver_assignment import FirestoreDriverAssignmentRepository


@pytest.mark.skipif(
    not os.getenv("FIRESTORE_EMULATOR_HOST"),
    reason="Requires Firestore emulator; never runs against live Firestore",
)
def test_driver_start_deliver_fail_complete_idempotency_and_ownership():
    from google.cloud import firestore

    db = firestore.Client(project="demo-smartroute")
    suffix = uuid4().hex[:12]
    uid = "synthetic-driver-" + suffix
    route_id = "synthetic-route-" + suffix
    order_ids = ["synthetic-order-" + suffix + "-1", "synthetic-order-" + suffix + "-2"]
    db.collection("users").document(uid).create({"uid": uid, "active": True, "role": "DRIVER"})
    db.collection("drivers").document(uid).create({
        "uid": uid, "active": True, "available": True, "display_name": "Emulator QA",
    })
    db.collection("routes").document(route_id).create({
        "id": route_id, "driver_id": uid, "route_type": "OPTIMIZED",
        "status": "PLANNED", "version": 2, "ordered_order_ids": order_ids,
        "depot": {"latitude": -12.095, "longitude": -77.035},
        "optimized_seconds": 600, "optimized_meters": 2500,
        "stop_snapshots": [{
            "id": oid, "address_label": "Synthetic stop",
            "geo": {"latitude": -12.1, "longitude": -77.04},
        } for oid in order_ids],
    })
    for oid in order_ids:
        db.collection("orders").document(oid).create({
            "id": oid, "route_id": route_id, "status": "ASSIGNED", "version": 2,
            "address_label": "Synthetic stop", "geo": {"latitude": -12.1, "longitude": -77.04},
        })
    db.collection("driver_assignments").document(uid).create({
        "driver_id": uid, "route_id": route_id, "status": "RESERVED", "version": 1,
    })

    workflow = FirestoreDriverWorkflowRepository(db)
    projection = FirestoreDriverAssignmentRepository(db)
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
