"""Route creation and atomic order assignment using Firestore server transactions."""
from google.cloud import firestore
from .routes import AssignmentConflict, RecordMissing, Route
from .firestore_config import firestore_client

class FirestoreRouteRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else firestore_client()

    def create(self, route: Route) -> None:
        driver = self.db.collection("drivers").document(route.driver_id).get()
        if not driver.exists:
            raise RecordMissing("Driver not found")
        self.db.collection("routes").document(route.id).create(route.model_dump(mode="python"))

    def assign(self, route_id: str, order_ids: list[str]) -> dict:
        if len(order_ids) != len(set(order_ids)):
            raise AssignmentConflict("Duplicated order IDs")
        if not 1 <= len(order_ids) <= 10:
            raise AssignmentConflict("Route needs 1–10 unique orders")
        route_ref = self.db.collection("routes").document(route_id)
        order_refs = [self.db.collection("orders").document(oid) for oid in sorted(order_ids)]

        @firestore.transactional
        def _apply(tx):
            # Firestore reads must precede ALL writes in the transaction.
            route_snap = route_ref.get(transaction=tx)
            if not route_snap.exists:
                raise RecordMissing("Route not found")
            route_data = route_snap.to_dict()
            if route_data.get("status") != "DRAFT":
                raise AssignmentConflict("Only DRAFT routes can accept orders")
            existing = list(route_data.get("order_ids") or [])
            if len(existing) + len(order_ids) > 10:
                raise AssignmentConflict("Maximum 10 stops")
            order_snaps = [ref.get(transaction=tx) for ref in order_refs]
            for snap in order_snaps:
                if not snap.exists:
                    raise RecordMissing("Order not found")
                data = snap.to_dict()
                if data.get("route_id") or data.get("status") != "PENDING":
                    raise AssignmentConflict("Order already assigned or not pending")
            now = firestore.SERVER_TIMESTAMP
            for ref in order_refs:
                tx.update(ref, {"route_id": route_id, "status": "ASSIGNED",
                                "updated_at": now, "version": firestore.Increment(1)})
            tx.update(route_ref, {"order_ids": existing + order_ids,
                                  "version": firestore.Increment(1)})
            return {"route_id": route_id, "order_ids": existing + order_ids, "assigned": len(order_ids)}

        return _apply(self.db.transaction())
