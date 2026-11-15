"""US-011: reserve one DRIVER for one optimized PLANNED route atomically.

This adapter has no public API registration yet; deploy only after emulator,
auth, gateway and contract tests. Firestore client targets named database via
firestore_config.firestore_client.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json

from google.cloud import firestore
from .driver_assignment import AssignDriverRequest
from .firestore_config import firestore_client
from .optimized_routes import OptimizedRoute


class DriverAssignmentConflict(Exception):
    """Stale version, occupied driver, or route already assigned."""


class DriverAssignmentMissing(Exception):
    """Route or DRIVER identity record does not exist."""


def _request_hash(payload: AssignDriverRequest) -> str:
    body = {"driver_id": payload.driver_id,
            "expected_version": payload.expected_version}
    return sha256(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()


class FirestoreDriverAssignmentRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else firestore_client()

    def assign(self, route_id: str, payload: AssignDriverRequest, *,
               operator_uid: str) -> OptimizedRoute:
        if not route_id or len(route_id) > 128 or "/" in route_id:
            raise DriverAssignmentMissing("Route not found")
        route_ref = self.db.collection("routes").document(route_id)
        user_ref = self.db.collection("users").document(payload.driver_id)
        driver_ref = self.db.collection("drivers").document(payload.driver_id)
        occupancy_ref = self.db.collection("driver_assignments").document(payload.driver_id)
        fingerprint = _request_hash(payload)
        key = str(payload.idempotency_key)

        @firestore.transactional
        def _commit(tx):
            # Read all references before ANY write: Firestore requirement.
            route_snap = route_ref.get(transaction=tx)
            user_snap = user_ref.get(transaction=tx)
            driver_snap = driver_ref.get(transaction=tx)
            occupancy_snap = occupancy_ref.get(transaction=tx)

            if not route_snap.exists:
                raise DriverAssignmentMissing("Route not found")
            route = route_snap.to_dict() or {}
            if route.get("route_type") != "OPTIMIZED":
                raise DriverAssignmentConflict("Not an optimized route")

            # Retry is allowed only for the same caller, key AND payload.
            if route.get("assignment_idempotency_key") == key:
                if (route.get("assignment_request_hash") != fingerprint
                    or route.get("assigned_by") != operator_uid):
                    raise DriverAssignmentConflict("Idempotency key reused")
                return OptimizedRoute.model_validate(route)

            if route.get("driver_id") is not None:
                raise DriverAssignmentConflict("Route already assigned")
            if route.get("status") != "PLANNED":
                raise DriverAssignmentConflict("Only PLANNED routes can be assigned")
            if route.get("version") != payload.expected_version:
                raise DriverAssignmentConflict("Route version changed")
            if not user_snap.exists or not driver_snap.exists:
                raise DriverAssignmentMissing("Driver profile not found")

            user = user_snap.to_dict() or {}
            driver = driver_snap.to_dict() or {}
            if (user.get("role") != "DRIVER" or user.get("active") is not True
                or driver.get("active") is not True
                or driver.get("available") is not True
                or driver.get("uid") != payload.driver_id):
                raise DriverAssignmentConflict("Driver inactive, invalid or unavailable")
            if occupancy_snap.exists:
                raise DriverAssignmentConflict("Driver already reserved")

            now = datetime.now(timezone.utc)
            next_version = payload.expected_version + 1
            tx.update(route_ref, {
                "driver_id": payload.driver_id,
                "assigned_by": operator_uid,
                "assigned_at": now,
                "updated_at": now,
                "version": next_version,
                "assignment_idempotency_key": key,
                "assignment_request_hash": fingerprint,
            })
            tx.create(occupancy_ref, {
                "driver_id": payload.driver_id,
                "route_id": route_id,
                "status": "RESERVED",
                "version": 1,
                "created_at": now,
                "updated_at": now,
            })
            return OptimizedRoute.model_validate({
                **route,
                "driver_id": payload.driver_id,
                "assigned_by": operator_uid,
                "assigned_at": now,
                "updated_at": now,
                "version": next_version,
            })

        return _commit(self.db.transaction())
