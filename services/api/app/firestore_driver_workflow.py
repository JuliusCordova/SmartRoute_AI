"""Transactional execution of a single driver's optimized route (US-012/013/014).

All documents are read BEFORE transaction writes. No external HTTP calls occur
inside retries. A keyed receipt is written atomically with route/order changes.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json

from google.cloud import firestore
from .driver_workflow import WorkflowRequest, StopResultRequest
from .firestore_config import firestore_client
from .qa_write_guard import enforce_qa_write_guard


class WorkflowConflict(Exception):
    """Invalid state, stale version, wrong owner or duplicated operation."""


class WorkflowMissing(Exception):
    """No route assigned, no such stop, or invalid identity."""


class FirestoreDriverWorkflowRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else firestore_client()

    def execute(self, *, driver_uid: str, action: str,
                payload: WorkflowRequest | StopResultRequest,
                order_id: str | None = None) -> dict:
        if not driver_uid or "/" in driver_uid or len(driver_uid) > 128:
            raise WorkflowMissing("Driver not found")
        if action not in {"start", "deliver", "fail", "complete"}:
            raise ValueError("Unsupported operation")
        if action in {"deliver", "fail"}:
            if not order_id or "/" in order_id or len(order_id) > 128:
                raise WorkflowMissing("Stop not found")
        elif order_id is not None:
            raise ValueError("Unexpected stop")

        reason = getattr(payload, "reason", None)
        if action == "fail" and (not reason or not reason.strip()):
            raise ValueError("Failure reason required")
        if action != "fail" and reason is not None:
            raise ValueError("Reason only allowed for failure")

        request = {
            "actor": driver_uid, "action": action, "order_id": order_id,
            "expected_version": payload.expected_version, "reason": reason,
        }
        fingerprint = sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        key = str(payload.idempotency_key)
        occupancy_ref = self.db.collection("driver_assignments").document(driver_uid)
        history_ref = self.db.collection("driver_last_routes").document(driver_uid)
        driver_ref = self.db.collection("drivers").document(driver_uid)
        user_ref = self.db.collection("users").document(driver_uid)

        @firestore.transactional
        def commit(tx):
            # Resolve route with transaction reads, including history for safe retries after completion.
            occupancy_snap = occupancy_ref.get(transaction=tx)
            history_snap = history_ref.get(transaction=tx)
            occupancy = occupancy_snap.to_dict() or {}
            history = history_snap.to_dict() or {}
            if occupancy_snap.exists:
                if occupancy.get("driver_id") != driver_uid or occupancy.get("status") not in ("RESERVED", "ACTIVE"):
                    raise WorkflowConflict("Inconsistent driver reservation")
                route_id = occupancy.get("route_id")
            else:
                route_id = history.get("route_id")
                if not route_id or action != "complete":
                    raise WorkflowMissing("No active route assigned")
            if not isinstance(route_id, str) or not route_id or "/" in route_id or len(route_id) > 128:
                raise WorkflowConflict("Invalid reservation route")

            # Check QA restriction against the reservation-resolved route before any writes.
            enforce_qa_write_guard(driver_uid=driver_uid, route_id=route_id)

            route_ref = self.db.collection("routes").document(route_id)
            event_id = sha256((driver_uid + ":" + route_id + ":" + key).encode()).hexdigest()
            event_ref = self.db.collection("driver_route_events").document(event_id)
            route_snap = route_ref.get(transaction=tx)
            event_snap = event_ref.get(transaction=tx)
            user_snap = user_ref.get(transaction=tx)
            driver_snap = driver_ref.get(transaction=tx)
            if not route_snap.exists:
                raise WorkflowMissing("Assigned route not found")
            route = route_snap.to_dict() or {}
            if (route.get("driver_id") != driver_uid
                or route.get("route_type") != "OPTIMIZED"):
                raise WorkflowConflict("Driver does not own route")
            if not user_snap.exists or not driver_snap.exists:
                raise WorkflowConflict("Driver identity unavailable")
            user, driver = user_snap.to_dict() or {}, driver_snap.to_dict() or {}
            if (user.get("role") != "DRIVER" or user.get("active") is not True
                or driver.get("uid") != driver_uid or driver.get("active") is not True):
                raise WorkflowConflict("Driver is inactive or invalid")

            # Immutable receipt: exact same actor/key/payload is safe to replay.
            if event_snap.exists:
                event = event_snap.to_dict() or {}
                if (event.get("fingerprint") != fingerprint
                    or event.get("actor_uid") != driver_uid
                    or event.get("route_id") != route_id):
                    raise WorkflowConflict("Idempotency key reused")
                return event["receipt"]

            if not occupancy_snap.exists:
                raise WorkflowConflict("Completed route cannot be mutated")
            if route.get("version") != payload.expected_version:
                raise WorkflowConflict("Stale route version")
            ids = route.get("ordered_order_ids") or []
            if (not 1 <= len(ids) <= 10 or len(set(ids)) != len(ids)
                or not all(isinstance(i, str) and i and "/" not in i for i in ids)):
                raise WorkflowConflict("Invalid route stops")

            order_refs = [self.db.collection("orders").document(i) for i in ids]
            order_snaps = [ref.get(transaction=tx) for ref in order_refs]
            if any(not snap.exists for snap in order_snaps):
                raise WorkflowConflict("Some route orders no longer exist")
            orders = [snap.to_dict() or {} for snap in order_snaps]
            if any(o.get("route_id") != route_id for o in orders):
                raise WorkflowConflict("Order ownership mismatch")

            new_status = route.get("status")
            new_orders: list[tuple[int, str]] = []
            receipt: dict
            if action == "start":
                if new_status != "PLANNED" or occupancy.get("status") != "RESERVED":
                    raise WorkflowConflict("Route cannot be started")
                if any(o.get("status") != "ASSIGNED" for o in orders):
                    raise WorkflowConflict("Unexpected order state")
                new_status = "ACTIVE"
                new_orders = [(i, "IN_TRANSIT") for i in range(len(ids))]
                receipt = {"id": route_id, "status": new_status, "version": payload.expected_version + 1}
            elif action in ("deliver", "fail"):
                if new_status != "ACTIVE" or occupancy.get("status") != "ACTIVE":
                    raise WorkflowConflict("Route is not active")
                if order_id not in ids:
                    raise WorkflowMissing("Stop not found on driver's route")
                index = ids.index(order_id)
                if orders[index].get("status") != "IN_TRANSIT":
                    raise WorkflowConflict("Stop already resolved or not in transit")
                destination = "DELIVERED" if action == "deliver" else "FAILED"
                new_orders = [(index, destination)]
                receipt = {
                    "id": route_id, "status": "ACTIVE", "version": payload.expected_version + 1,
                    "order_id": order_id, "order_status": destination,
                }
            else:
                if new_status != "ACTIVE" or occupancy.get("status") != "ACTIVE":
                    raise WorkflowConflict("Route is not active")
                if any(o.get("status") not in ("DELIVERED", "FAILED") for o in orders):
                    raise WorkflowConflict("Pending stops prevent completion")
                new_status = "COMPLETED"
                receipt = {"id": route_id, "status": new_status, "version": payload.expected_version + 1}

            now = datetime.now(timezone.utc)
            route_patch = {
                "status": new_status, "version": payload.expected_version + 1,
                "updated_at": now,
            }
            if action == "start":
                route_patch["started_at"] = now
            if action == "complete":
                route_patch["completed_at"] = now
                route_patch["completed_summary"] = {
                    "delivered": sum(o.get("status") == "DELIVERED" for o in orders),
                    "failed": sum(o.get("status") == "FAILED" for o in orders),
                    "total": len(ids),
                }

            # All Firestore reads finished. Mutations below are atomic.
            tx.update(route_ref, route_patch)
            for index, destination in new_orders:
                patch = {
                    "status": destination, "updated_at": now,
                    "version": firestore.Increment(1),
                }
                if destination in ("DELIVERED", "FAILED"):
                    patch["resolved_at"] = now
                    patch["resolved_by"] = driver_uid
                    if destination == "FAILED":
                        patch["failure_reason"] = reason
                tx.update(order_refs[index], patch)

            if action == "start":
                tx.update(occupancy_ref, {
                    "status": "ACTIVE", "updated_at": now,
                    "version": firestore.Increment(1),
                })
                tx.update(driver_ref, {"available": False, "updated_at": now})
            if action == "complete":
                tx.delete(occupancy_ref)
                tx.update(driver_ref, {"available": True, "updated_at": now})
                tx.set(history_ref, {
                    "route_id": route_id, "driver_id": driver_uid,
                    "completed_at": now,
                })
            tx.create(event_ref, {
                "actor_uid": driver_uid, "route_id": route_id,
                "action": action, "order_id": order_id,
                "fingerprint": fingerprint, "idempotency_key": key,
                "receipt": receipt, "created_at": now,
            })
            return receipt

        return commit(self.db.transaction())
