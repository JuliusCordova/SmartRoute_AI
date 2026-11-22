"""US-017 route reference is optional and preserves legacy idempotency."""
from hashlib import sha256
import json
from uuid import uuid4
from app.optimized_routes import OptimizedRouteCreate
from app.firestore_optimized_routes import _payload_hash


def test_legacy_route_idempotency_hash_unchanged():
    payload = OptimizedRouteCreate(
        depot={"latitude": -12.095, "longitude": -77.035},
        order_ids=["order-a"], idempotency_key=uuid4(),
    )
    legacy = sha256(json.dumps(
        {"depot": payload.depot.model_dump(), "order_ids": payload.order_ids},
        sort_keys=True,
    ).encode()).hexdigest()
    assert _payload_hash(payload) == legacy


def test_center_association_changes_route_request_fingerprint():
    common = dict(depot={"latitude": -12.095, "longitude": -77.035},
                  order_ids=["order-a"], idempotency_key=uuid4())
    legacy = OptimizedRouteCreate(**common)
    selected = OptimizedRouteCreate(**common, distribution_center_id="site-one")
    assert _payload_hash(legacy) != _payload_hash(selected)
