"""US-011: reserve one DRIVER for one optimized PLANNED route atomically.

This adapter has no public API registration yet; deploy only after emulator,
auth, gateway and contract tests. Firestore client targets named database via
firestore_config.firestore_client.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json

from google.cloud import firestore
from .driver_assignment import AssignDriverRequest, DriverRoute, DriverStop
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


    def own_route(self, *, driver_uid: str) -> DriverRoute | None:
        """Read only via trusted UID extracted from a verified Firebase DRIVER.

        Lookup is keyed by driver_assignments/{uid}, never by caller-supplied
        route ID. No ORS calls, mutation, or global collection listing.
        """
        if not driver_uid or "/" in driver_uid or len(driver_uid) > 128:
            raise DriverAssignmentConflict("Invalid driver identity")
        occupancy = self.db.collection("driver_assignments").document(driver_uid).get()
        if not occupancy.exists:
            return None
        reservation = occupancy.to_dict() or {}
        route_id = reservation.get("route_id")
        if (reservation.get("driver_id") != driver_uid
            or reservation.get("status") != "RESERVED"
            or not isinstance(route_id, str) or not route_id or "/" in route_id):
            raise DriverAssignmentConflict("Invalid driver reservation")
        snap = self.db.collection("routes").document(route_id).get()
        if not snap.exists:
            raise DriverAssignmentConflict("Assigned route is unavailable")
        route = snap.to_dict() or {}
        if (route.get("driver_id") != driver_uid
            or route.get("route_type") != "OPTIMIZED"
            or route.get("status") not in ("PLANNED", "ACTIVE")):
            raise DriverAssignmentConflict("Assigned route is not accessible")

        ordered_ids = route.get("ordered_order_ids") or []
        if (not 1 <= len(ordered_ids) <= 10
            or len(set(ordered_ids)) != len(ordered_ids)):
            raise DriverAssignmentConflict("Invalid saved route stops")
        snapshots = route.get("stop_snapshots") or []
        by_id = {x["id"]: x for x in snapshots
                 if isinstance(x, dict) and isinstance(x.get("id"), str)}
        # Legacy route saved before the snapshot implementation: resolve only
        # the exact orders belonging to the assigned route.
        for oid in ordered_ids:
            if oid not in by_id:
                order_snap = self.db.collection("orders").document(oid).get()
                if not order_snap.exists:
                    raise DriverAssignmentConflict("Assigned stop not found")
                data = order_snap.to_dict() or {}
                if data.get("route_id") != route_id:
                    raise DriverAssignmentConflict("Stop does not belong to route")
                by_id[oid] = {
                    "id": oid, "address_label": data.get("address_label"),
                    "geo": data.get("geo"),
                }
        try:
            stops = [DriverStop(
                sequence=index, order_id=oid,
                address_label=by_id[oid]["address_label"],
                geo=by_id[oid]["geo"],
            ) for index, oid in enumerate(ordered_ids, start=1)]
            return DriverRoute(
                id=route_id, status=route["status"],
                depot=route["depot"], stops=stops,
                optimized_seconds=route["optimized_seconds"],
                optimized_meters=route["optimized_meters"],
                assigned_at=route.get("assigned_at"),
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise DriverAssignmentConflict("Invalid assigned route data") from exc
