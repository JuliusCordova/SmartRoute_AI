"""US-010: Firestore adapter with atomic route creation and order reservation.

All reads happen before any transaction write. Road matrix calls happen before
transaction; recheck order versions and coordinates before committing.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from uuid import uuid5, NAMESPACE_URL
import httpx

from google.cloud import firestore
from .firestore_config import firestore_client
from .orders import Geo
from .optimized_routes import (
    OptimizedRoute, OptimizedRouteConflict, OptimizedRouteCreate,
    OptimizedRouteMissing, OptimizedRoutePage, OptimizedRouteDetail, PersistedStop,
)
from .route_preview import PreviewRequest, StopPoint, compute_preview, ORS_DIRECTIONS


def _payload_hash(payload: OptimizedRouteCreate) -> str:
    return sha256(json.dumps(
        dict({"depot": payload.depot.model_dump(), "order_ids": payload.order_ids},
             **({"distribution_center_id": payload.distribution_center_id} if payload.distribution_center_id else {})),
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

    def detail(self, route_id: str) -> OptimizedRouteDetail:
        """Resolve stop labels and road trace without changing the saved solution.

        Legacy saved routes without snapshots use the current order records.
        The original ordered_order_ids and estimated metrics are immutable.
        """
        route = self.get(route_id)
        saved = self.db.collection("routes").document(route_id).get().to_dict() or {}
        snapshots = saved.get("stop_snapshots") or []
        by_id = {s["id"]: s for s in snapshots if isinstance(s, dict) and s.get("id")}
        missing_ids = [oid for oid in route.ordered_order_ids if oid not in by_id]
        if missing_ids:
            refs = [self.db.collection("orders").document(oid) for oid in missing_ids]
            for oid, snap in zip(missing_ids, (ref.get() for ref in refs)):
                if snap.exists:
                    doc = snap.to_dict() or {}
                    by_id[oid] = {"id": oid, "address_label": doc.get("address_label") or oid, "geo": doc.get("geo")}

        stops = []
        warnings = []
        for index, oid in enumerate(route.ordered_order_ids, start=1):
            info = by_id.get(oid)
            if not info or not info.get("geo"):
                warnings.append("Some saved stops are unavailable; the route cannot be traced fully")
                continue
            stops.append(PersistedStop(
                id=oid, address_label=info.get("address_label") or oid,
                geo=Geo.model_validate(info["geo"]), sequence=index,
            ))
        road = None
        origin = "schematic"
        key = os.getenv("ORS_API_KEY")
        if key and len(stops) == len(route.ordered_order_ids):
            coords = [
                [route.depot.longitude, route.depot.latitude],
                *[[stop.geo.longitude, stop.geo.latitude] for stop in stops],
                [route.depot.longitude, route.depot.latitude],
            ]
            try:
                with httpx.Client(timeout=8.0) as client:
                    resp = client.post(
                        ORS_DIRECTIONS,
                        json={"coordinates": coords},
                        headers={"Authorization": key, "Content-Type": "application/json"},
                    )
                    resp.raise_for_status()
                    features = resp.json().get("features", [])
                coordinates = features[0]["geometry"]["coordinates"] if features else None
                if (isinstance(coordinates, list) and 2 <= len(coordinates) <= 20000
                    and all(isinstance(x, list) and len(x) >= 2 for x in coordinates)):
                    road = [[float(x[0]), float(x[1])] for x in coordinates]
                    origin = "openrouteservice"
            except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError):
                warnings.append("Road geometry unavailable; schematic connectors shown")
        else:
            warnings.append("Road geometry not requested; schematic connectors shown")
        if road is None and not warnings:
            warnings.append("Road geometry unavailable; schematic connectors shown")
        return OptimizedRouteDetail(
            **route.model_dump(mode="python"),
            stops=stops, route_geometry=road, geometry_origin=origin,
            detail_warnings=warnings,
        )

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

        center_ref = None
        center_record = None
        if payload.distribution_center_id:
            if "/" in payload.distribution_center_id:
                raise OptimizedRouteConflict("Invalid center identifier")
            center_ref = self.db.collection("distribution_centers").document(payload.distribution_center_id)
            center_snap = center_ref.get()
            if not center_snap.exists:
                raise OptimizedRouteMissing("Centro no encontrado")
            center_record = center_snap.to_dict() or {}
            if not center_record.get("active", False):
                raise OptimizedRouteConflict("Centro inactivo")
            if center_record.get("geo") != payload.depot.model_dump():
                raise OptimizedRouteConflict("El origen no coincide con la sede seleccionada")
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
            distribution_center_id=payload.distribution_center_id,
            distribution_center_name=center_record.get("name") if center_record else None,
            order_ids=payload.order_ids, baseline_order_ids=payload.order_ids,
            ordered_order_ids=preview.ordered_order_ids,
            baseline_seconds=preview.baseline_seconds, optimized_seconds=preview.optimized_seconds,
            baseline_meters=preview.baseline_meters, optimized_meters=preview.optimized_meters,
            improvement_pct=preview.improvement_pct,
            matrix_fingerprint=preview.matrix_fingerprint,
            matrix_provider=preview.matrix_provider, data_origin=preview.data_origin,
            warnings=preview.warnings, created_at=now, updated_at=now,
        )
        route_record = {
            **route.model_dump(mode="python"),
            "request_hash": fingerprint,
            "stop_snapshots": [
                {"id": oid, "address_label": data["address_label"], "geo": data["geo"]}
                for oid, data in zip(payload.order_ids, original)
            ],
        }

        @firestore.transactional
        def _commit(tx):
            current_route = route_ref.get(transaction=tx)
            current_orders = [ref.get(transaction=tx) for ref in order_refs]
            if center_ref is not None:
                current_center_snap = center_ref.get(transaction=tx)
                if not current_center_snap.exists:
                    raise OptimizedRouteConflict("Centro eliminado durante la optimizacion")
                current_center = current_center_snap.to_dict() or {}
                if (not current_center.get("active") or
                    current_center.get("version") != center_record.get("version") or
                    current_center.get("geo") != payload.depot.model_dump()):
                    raise OptimizedRouteConflict("Centro cambiado durante la optimizacion")
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
