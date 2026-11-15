"""US-010: Firestore adapter with atomic route creation and order reservation.

All reads happen before any transaction write. Road matrix calls happen before
transaction; recheck order versions and coordinates before committing.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
from uuid import uuid5, NAMESPACE_URL

from google.cloud import firestore
from .firestore_config import firestore_client
from .orders import Geo
from .optimized_routes import (
    OptimizedRoute, OptimizedRouteConflict, OptimizedRouteCreate,
    OptimizedRouteMissing, OptimizedRoutePage,
)
from .route_preview import PreviewRequest, StopPoint, compute_preview


def _payload_hash(payload: OptimizedRouteCreate) -> str:
    return sha256(json.dumps(
        {"depot": payload.depot.model_dump(), "order_ids": payload.order_ids},
        sort_keys=True,
    ).encode()).hexdigest()


class FirestoreOptimizedRouteRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else firestore_client()

    def get(self, route_id: str) -> OptimizedRoute:
        if not route_id or len(route_id) > 128 or "/" in route_id:
            raise OptimizedRouteMissing("Route not found")
        snap = self.db.collection("routes").document(route_id).get()
        if not snap.exists or (snap.to_dict() or {}).get("route_type") != "OPTIMIZED":
            raise OptimizedRouteMissing("Route not found")
        return OptimizedRoute.model_validate(snap.to_dict())

    def list(self, *, limit: int, after: str | None) -> OptimizedRoutePage:
        coll = self.db.collection("routes")
        query = coll.where("route_type", "==", "OPTIMIZED").order_by("__name__")
        if after:
            prior = coll.document(after).get()
            if not prior.exists or (prior.to_dict() or {}).get("route_type") != "OPTIMIZED":
                raise ValueError("Invalid cursor")
            query = query.start_after(prior)
        docs = list(query.limit(limit + 1).stream())
        selected = docs[:limit]
        return OptimizedRoutePage(
            items=[OptimizedRoute.model_validate(doc.to_dict()) for doc in selected],
            next_cursor=selected[-1].id if len(docs) > limit and selected else None,
        )

    def save(self, payload: OptimizedRouteCreate, *, actor_uid: str) -> tuple[OptimizedRoute, bool]:
        fingerprint = _payload_hash(payload)
        route_id = str(uuid5(NAMESPACE_URL, "smartroute:optimized:" + actor_uid + ":" + str(payload.idempotency_key)))
        route_ref = self.db.collection("routes").document(route_id)
        existing = route_ref.get()
        if existing.exists:
            saved = existing.to_dict()
            if saved.get("request_hash") != fingerprint or saved.get("created_by") != actor_uid:
                raise OptimizedRouteConflict("Idempotency key reused for a different request")
            return OptimizedRoute.model_validate(saved), False

        order_refs = [self.db.collection("orders").document(oid) for oid in payload.order_ids]
        docs = [ref.get() for ref in order_refs]
        if any(not snap.exists for snap in docs):
            raise OptimizedRouteMissing("Order not found")
        original = [snap.to_dict() for snap in docs]
        if any(d.get("status") != "PENDING" or d.get("route_id") for d in original):
            raise OptimizedRouteConflict("Order already reserved or not pending")
        positions = [Geo.model_validate(d["geo"]) for d in original]
        req = PreviewRequest(
            depot=StopPoint(id="__depot__", latitude=payload.depot.latitude, longitude=payload.depot.longitude),
            stops=[StopPoint(id=oid, latitude=pos.latitude, longitude=pos.longitude)
                   for oid, pos in zip(payload.order_ids, positions)],
        )
        preview = compute_preview(req)
        if set(preview.ordered_order_ids) != set(payload.order_ids) or len(preview.ordered_order_ids) != len(payload.order_ids):
            raise OptimizedRouteConflict("Solver returned an invalid order sequence")

        now = datetime.now(timezone.utc)
        route = OptimizedRoute(
            id=route_id, created_by=actor_uid, depot=payload.depot,
            order_ids=payload.order_ids, baseline_order_ids=payload.order_ids,
            ordered_order_ids=preview.ordered_order_ids,
            baseline_seconds=preview.baseline_seconds, optimized_seconds=preview.optimized_seconds,
            baseline_meters=preview.baseline_meters, optimized_meters=preview.optimized_meters,
            improvement_pct=preview.improvement_pct,
            matrix_fingerprint=preview.matrix_fingerprint,
            matrix_provider=preview.matrix_provider, data_origin=preview.data_origin,
            warnings=preview.warnings, created_at=now, updated_at=now,
        )
        route_record = {**route.model_dump(mode="python"), "request_hash": fingerprint}

        @firestore.transactional
        def _commit(tx):
            current_route = route_ref.get(transaction=tx)
            current_orders = [ref.get(transaction=tx) for ref in order_refs]
            if current_route.exists:
                saved = current_route.to_dict()
                if saved.get("request_hash") != fingerprint or saved.get("created_by") != actor_uid:
                    raise OptimizedRouteConflict("Idempotency key reused for a different request")
                return OptimizedRoute.model_validate(saved), False
            for before, current in zip(original, current_orders):
                if not current.exists:
                    raise OptimizedRouteConflict("Order removed during optimization")
                latest = current.to_dict()
                if (latest.get("status") != "PENDING" or latest.get("route_id")
                    or latest.get("version") != before.get("version")
                    or latest.get("geo") != before.get("geo")):
                    raise OptimizedRouteConflict("Order changed during optimization")
            tx.create(route_ref, route_record)
            for ref in order_refs:
                tx.update(ref, {
                    "route_id": route_id, "status": "ASSIGNED",
                    "updated_at": firestore.SERVER_TIMESTAMP,
                    "version": firestore.Increment(1),
                })
            return route, True

        return _commit(self.db.transaction())
