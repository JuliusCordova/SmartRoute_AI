"""US-011 Firestore Emulator tests; no live GCP or external identity calls."""
import os
from datetime import datetime, timezone
from uuid import uuid4
import pytest


@pytest.fixture
def setup_assignment():
    if not os.environ.get("FIRESTORE_EMULATOR_HOST"):
        if os.environ.get("FIRESTORE_EMULATOR_REQUIRED") == "1":
            pytest.fail("FIRESTORE_EMULATOR_HOST required")
        pytest.skip("Firestore emulator required")
    from google.cloud import firestore
    from app.optimized_routes import OptimizedRoute
    from app.firestore_driver_assignment import FirestoreDriverAssignmentRepository
    db = firestore.Client(project="demo-smartroute")
    suffix = uuid4().hex
    driver_id = "synthetic-driver-" + suffix
    now = datetime.now(timezone.utc)
    route = OptimizedRoute(
        id=str(uuid4()), created_by="synthetic-operator",
        depot={"latitude": -12.095, "longitude": -77.035},
        order_ids=["order-1"], baseline_order_ids=["order-1"],
        ordered_order_ids=["order-1"], baseline_seconds=300,
        optimized_seconds=270, baseline_meters=4500, optimized_meters=4300,
        improvement_pct=10.0, matrix_fingerprint="a"*64,
        created_at=now, updated_at=now,
    )
    db.collection("users").document(driver_id).create({"role": "DRIVER", "active": True})
    db.collection("drivers").document(driver_id).create({
        "uid": driver_id, "display_name": "Conductor sintético",
        "active": True, "available": True,
    })
    db.collection("routes").document(route.id).create(route.model_dump(mode="python"))
    return db, FirestoreDriverAssignmentRepository(db), route, driver_id


def test_atomic_assignment_preserves_metrics_and_rejects_stale_retry(setup_assignment):
    from app.driver_assignment import AssignDriverRequest
    from app.firestore_driver_assignment import DriverAssignmentConflict
    db, repo, route, driver_id = setup_assignment
    req = AssignDriverRequest(driver_id=driver_id, expected_version=1,
                              idempotency_key=uuid4())
    assigned = repo.assign(route.id, req, operator_uid="synthetic-operator")
    assert assigned.driver_id == driver_id
    assert assigned.status == "PLANNED" and assigned.version == 2
    assert assigned.ordered_order_ids == route.ordered_order_ids
    assert assigned.optimized_meters == route.optimized_meters
    assert repo.assign(route.id, req, operator_uid="synthetic-operator").id == route.id
    occupant = db.collection("driver_assignments").document(driver_id).get().to_dict()
    assert occupant["route_id"] == route.id and occupant["status"] == "RESERVED"
    with pytest.raises(DriverAssignmentConflict):
        repo.assign(route.id, AssignDriverRequest(
            driver_id=driver_id, expected_version=1, idempotency_key=uuid4()),
            operator_uid="synthetic-operator")
    assert db.collection("routes").document(route.id).get().to_dict()["version"] == 2


def test_same_driver_cannot_be_reserved_by_two_routes(setup_assignment):
    from app.driver_assignment import AssignDriverRequest
    from app.firestore_driver_assignment import DriverAssignmentConflict
    db, repo, route, driver_id = setup_assignment
    other_id = str(uuid4())
    other = db.collection("routes").document(route.id).get().to_dict()
    other["id"] = other_id
    db.collection("routes").document(other_id).create(other)
    first_req = AssignDriverRequest(driver_id=driver_id, expected_version=1,
                                    idempotency_key=uuid4())
    repo.assign(route.id, first_req, operator_uid="synthetic-operator")
    with pytest.raises(DriverAssignmentConflict):
        repo.assign(other_id, AssignDriverRequest(
            driver_id=driver_id, expected_version=1, idempotency_key=uuid4()),
            operator_uid="synthetic-operator")
    assert db.collection("routes").document(other_id).get().to_dict()["driver_id"] is None


def test_inactive_driver_causes_no_mutation(setup_assignment):
    from app.driver_assignment import AssignDriverRequest
    from app.firestore_driver_assignment import DriverAssignmentConflict
    db, repo, route, driver_id = setup_assignment
    db.collection("users").document(driver_id).update({"active": False})
    with pytest.raises(DriverAssignmentConflict):
        repo.assign(route.id, AssignDriverRequest(
            driver_id=driver_id, expected_version=1, idempotency_key=uuid4()),
            operator_uid="synthetic-operator")
    assert db.collection("routes").document(route.id).get().to_dict()["driver_id"] is None
    assert not db.collection("driver_assignments").document(driver_id).get().exists
