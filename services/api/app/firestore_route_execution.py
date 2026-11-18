"""US-012: atomic DRIVER-owned PLANNED -> ACTIVE transition.

The verified caller UID, never a client route_id, selects the occupancy record.
All Firestore reads precede writes inside each transaction.
"""
from datetime import datetime, timezone
from uuid import uuid5, NAMESPACE_URL

from google.cloud import firestore
from .firestore_config import firestore_client
from .route_execution import (
    RouteExecutionResult, RouteExecutionMissing, RouteExecutionConflict,
    StartRouteRequest,
)


class FirestoreRouteExecutionRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else firestore_client()

    def start(self, *, driver_uid: str, payload: StartRouteRequest) -> RouteExecutionResult:
        if not driver_uid or len(driver_uid) > 128 or "/" in driver_uid:
            raise RouteExecutionConflict("Invalid driver identity")
        reservation_ref = self.db.collection("driver_assignments").document(driver_uid)
        user_ref = self.db.collection("users").document(driver_uid)
        driver_ref = self.db.collection("drivers").document(driver_uid)
        key = str(payload.idempotency_key)

        @firestore.transactional
        def _commit(tx):
            occupancy_snap = reservation_ref.get(transaction=tx)
            if not occupancy_snap.exists:
                raise RouteExecutionMissing("No assigned route")
            occupancy = occupancy_snap.to_dict() or {}
            route_id = occupancy.get("route_id")
            if (occupancy.get("driver_id") != driver_uid
                    or not isinstance(route_id, str)
                    or not route_id or len(route_id) > 128 or "/" in route_id):
                raise RouteExecutionConflict("Invalid driver reservation")
            route_ref = self.db.collection("routes").document(route_id)
            route_snap = route_ref.get(transaction=tx)
            user_snap = user_ref.get(transaction=tx)
            driver_snap = driver_ref.get(transaction=tx)
            if not route_snap.exists:
                raise RouteExecutionConflict("Assigned route missing")
            if not user_snap.exists or not driver_snap.exists:
                raise RouteExecutionConflict("Driver profile missing")
            user = user_snap.to_dict() or {}
            driver = driver_snap.to_dict() or {}
            route = route_snap.to_dict() or {}
            if (user.get("role") != "DRIVER" or user.get("active") is not True
                    or driver.get("uid") != driver_uid
                    or driver.get("active") is not True
                    or route.get("route_type") != "OPTIMIZED"
                    or route.get("driver_id") != driver_uid):
                raise RouteExecutionConflict("Driver or route not permitted")

            # Repeated same request is a read-only success even after activation.
            if route.get("execution_start_key") == key:
                if (route.get("execution_start_expected_version") != payload.expected_version
                        or route.get("started_by") != driver_uid
                        or route.get("status") != "ACTIVE"
                        or occupancy.get("status") != "ACTIVE"
                        or occupancy.get("route_id") != route_id):
                    raise RouteExecutionConflict("Idempotency key reused or inconsistent state")
                return RouteExecutionResult(
                    id=route_id, driver_id=driver_uid, status="ACTIVE",
                    version=route["version"], started_at=route["started_at"],
                )

            if (route.get("status") != "PLANNED"
                    or occupancy.get("status") != "RESERVED"):
                raise RouteExecutionConflict("Route not ready to start")
            if route.get("version") != payload.expected_version:
                raise RouteExecutionConflict("Route version changed")

            now = datetime.now(timezone.utc)
            next_version = payload.expected_version + 1
            event_id = str(uuid5(NAMESPACE_URL,
                                 f"smartroute:start:{route_id}:{driver_uid}:{key}"))
            event_ref = self.db.collection("route_events").document(event_id)
            tx.update(route_ref, {
                "status": "ACTIVE",
                "version": next_version,
                "started_by": driver_uid,
                "started_at": now,
                "updated_at": now,
                "execution_start_key": key,
                "execution_start_expected_version": payload.expected_version,
            })
            tx.update(reservation_ref, {
                "status": "ACTIVE",
                "version": firestore.Increment(1),
                "started_at": now,
                "updated_at": now,
            })
            tx.create(event_ref, {
                "route_id": route_id,
                "driver_id": driver_uid,
                "actor_uid": driver_uid,
                "event_type": "ROUTE_STARTED",
                "before_status": "PLANNED",
                "after_status": "ACTIVE",
                "route_version": next_version,
                "occurred_at": now,
            })
            return RouteExecutionResult(
                id=route_id, driver_id=driver_uid, status="ACTIVE",
                version=next_version, started_at=now,
            )

        return _commit(self.db.transaction())
