"""Real Firestore SDK against the local emulator; never uses GCP production."""
import os
from uuid import uuid4
import pytest

def test_create_and_page_against_firestore_emulator():
    if not os.environ.get("FIRESTORE_EMULATOR_HOST"):
        if os.environ.get("FIRESTORE_EMULATOR_REQUIRED") == "1":
            pytest.fail("FIRESTORE_EMULATOR_HOST is required by CI integration job")
        pytest.skip("Only run against local Firestore emulator")
    from google.cloud import firestore
    from app.firestore_repo import FirestoreOrderRepository
    from app.orders import Geo, OrderCreate, new_order

    db = firestore.Client(project="demo-smartroute")
    repo = FirestoreOrderRepository(db)
    prefix = "E2E-synthetic-" + uuid4().hex[:12]
    orders = []
    for i in range(3):
        payload = OrderCreate(address_label=f"{prefix}-{i}", geo=Geo(latitude=-12.09, longitude=-77.04))
        order = new_order(payload, actor_uid="synthetic-operator")
        repo.create(order)
        orders.append(order)
    # Emulated Firestore collections may contain data from other tests: query IDs, not global counts.
    for o in orders:
        snap = db.collection("orders").document(o.id).get()
        assert snap.exists
        assert snap.to_dict()["status"] == "PENDING"
        assert snap.to_dict()["data_origin"] == "synthetic"
    # Page contract is checked with an isolated query on document ID; page cap is respected.
    page = repo.list(limit=2, after=None)
    assert len(page.items) <= 2
    if page.next_cursor:
        page2 = repo.list(limit=2, after=page.next_cursor)
        assert page2.items
