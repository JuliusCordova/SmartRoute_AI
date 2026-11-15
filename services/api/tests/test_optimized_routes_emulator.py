"""US-010 Firestore emulator integration tests.

No live GCP calls. CI may set FIRESTORE_EMULATOR_REQUIRED=1.
"""
import os
from uuid import uuid4
import pytest


def test_atomic_save_reserves_orders_and_retries(monkeypatch):
    if not os.environ.get("FIRESTORE_EMULATOR_HOST"):
        if os.environ.get("FIRESTORE_EMULATOR_REQUIRED") == "1":
            pytest.fail("FIRESTORE_EMULATOR_HOST required for integration")
        pytest.skip("Requires Firestore emulator")
    from google.cloud import firestore
    from app.orders import OrderCreate, new_order
    from app.optimized_routes import OptimizedRouteCreate, OptimizedRouteConflict
    from app.firestore_optimized_routes import FirestoreOptimizedRouteRepository
    from app.route_preview import PreviewResult
    import app.firestore_optimized_routes as module

    db = firestore.Client(project="demo-smartroute")
    repo = FirestoreOptimizedRouteRepository(db)
    suffix = uuid4().hex[:12]
    ids = []
    for i in range(2):
        order = new_order(OrderCreate(
            address_label=f"Synthetic Lima stop {suffix}-{i}",
            geo={"latitude": -12.10 - i * 0.01, "longitude": -77.04 - i * 0.01},
        ), actor_uid="synthetic")
        db.collection("orders").document(order.id).create(order.model_dump(mode="python"))
        ids.append(order.id)

    calls = []
    def fake_preview(req):
        calls.append(req)
        return PreviewResult(
            ordered_order_ids=list(reversed(ids)), baseline_seconds=300,
            optimized_seconds=270, baseline_meters=4500, optimized_meters=4300,
            improvement_pct=10.0, matrix_fingerprint="a" * 64,
            route_geometry=None, warnings=["Estimated only"],
        )
    monkeypatch.setattr(module, "compute_preview", fake_preview)
    payload = OptimizedRouteCreate(depot={"latitude": -12.095, "longitude": -77.035},
                                   order_ids=ids, idempotency_key=uuid4())
    first, created = repo.save(payload, actor_uid="synthetic-operator")
    assert created and first.status == "PLANNED" and first.driver_id is None
    assert first.ordered_order_ids == ids[::-1]
    assert len(calls) == 1
    loaded = repo.get(first.id)
    assert loaded.ordered_order_ids == ids[::-1]
    assert loaded.matrix_provider == "openrouteservice"
    for order_id in ids:
        doc = db.collection("orders").document(order_id).get().to_dict()
        assert doc["route_id"] == first.id
        assert doc["status"] == "ASSIGNED" and doc["version"] == 2
    again, created = repo.save(payload, actor_uid="synthetic-operator")
    assert not created and again.id == first.id and len(calls) == 1
    assert repo.list(limit=10, after=None).items

    conflict_payload = OptimizedRouteCreate(
        depot=payload.depot, order_ids=list(reversed(ids)), idempotency_key=uuid4())
    with pytest.raises(OptimizedRouteConflict):
        repo.save(conflict_payload, actor_uid="synthetic-operator")
    assert all(db.collection("orders").document(x).get().to_dict()["route_id"] == first.id for x in ids)


def test_concurrent_order_state_change_causes_no_partial_save(monkeypatch):
    if not os.environ.get("FIRESTORE_EMULATOR_HOST"):
        pytest.skip("Requires Firestore emulator")
    from google.cloud import firestore
    from app.orders import OrderCreate, new_order
    from app.optimized_routes import OptimizedRouteCreate, OptimizedRouteConflict
    from app.firestore_optimized_routes import FirestoreOptimizedRouteRepository
    from app.route_preview import PreviewResult
    import app.firestore_optimized_routes as module

    db = firestore.Client(project="demo-smartroute")
    order = new_order(OrderCreate(
        address_label="Synthetic race stop", geo={"latitude": -12.1, "longitude": -77.04},
    ), actor_uid="synthetic")
    db.collection("orders").document(order.id).create(order.model_dump(mode="python"))
    repo = FirestoreOptimizedRouteRepository(db)

    def change_during_solver(req):
        db.collection("orders").document(order.id).update({
            "status": "ASSIGNED", "route_id": "other-route", "version": firestore.Increment(1),
        })
        return PreviewResult(
            ordered_order_ids=[order.id], baseline_seconds=120, optimized_seconds=120,
            baseline_meters=300, optimized_meters=300, improvement_pct=0.0,
            matrix_fingerprint="b" * 64, warnings=[],
        )

    monkeypatch.setattr(module, "compute_preview", change_during_solver)
    payload = OptimizedRouteCreate(depot={"latitude": -12.095, "longitude": -77.035},
                                   order_ids=[order.id], idempotency_key=uuid4())
    with pytest.raises(OptimizedRouteConflict):
        repo.save(payload, actor_uid="synthetic-operator")
    route_id = str(__import__("uuid").uuid5(
        __import__("uuid").NAMESPACE_URL,
        "smartroute:optimized:synthetic-operator:" + str(payload.idempotency_key),
    ))
    assert not db.collection("routes").document(route_id).get().exists
    assert db.collection("orders").document(order.id).get().to_dict()["route_id"] == "other-route"
