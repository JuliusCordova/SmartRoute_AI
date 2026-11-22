"""Firestore adapter for named SmartRoute database only. No cloud access at import time."""
from datetime import datetime, timezone

from google.cloud import firestore
from .firestore_config import firestore_client
from .distribution_centers import (
    CenterPage, CenterCreate, CenterUpdate, CenterNotFound, CenterConflict,
    DistributionCenter, create_center,
)


class FirestoreCenterRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else firestore_client()

    @staticmethod
    def _ref_id(center_id: str):
        if not isinstance(center_id, str) or not center_id or len(center_id) > 128 or "/" in center_id:
            raise CenterNotFound("Centro no encontrado")
        return center_id

    def list(self, *, limit: int, after: str | None) -> CenterPage:
        coll = self.db.collection("distribution_centers")
        query = coll.order_by("__name__")
        if after:
            prior = coll.document(self._ref_id(after)).get()
            if not prior.exists:
                raise ValueError("Cursor invalido")
            query = query.start_after(prior)
        docs = list(query.limit(limit + 1).stream())
        return CenterPage(
            items=[DistributionCenter.model_validate(s.to_dict()) for s in docs[:limit]],
            next_cursor=docs[limit - 1].id if len(docs) > limit else None,
        )

    def get(self, center_id: str) -> DistributionCenter:
        snap = self.db.collection("distribution_centers").document(self._ref_id(center_id)).get()
        if not snap.exists:
            raise CenterNotFound("Centro no encontrado")
        return DistributionCenter.model_validate(snap.to_dict())

    def create(self, payload: CenterCreate, *, actor_uid: str) -> DistributionCenter:
        center = create_center(payload, actor_uid)
        center_ref = self.db.collection("distribution_centers").document(center.id)
        # Permanent unique code: deactivating a center does not permit code reuse.
        code_ref = self.db.collection("distribution_center_codes").document(center.code)
        @firestore.transactional
        def apply(tx):
            if code_ref.get(transaction=tx).exists:
                raise CenterConflict("Codigo de sede ya registrado")
            tx.create(code_ref, {"center_id": center.id})
            tx.create(center_ref, center.model_dump(mode="python"))
        apply(self.db.transaction())
        return center

    def update(self, center_id: str, payload: CenterUpdate) -> DistributionCenter:
        self._ref_id(center_id)
        payload.ensure_valid()
        ref = self.db.collection("distribution_centers").document(center_id)
        @firestore.transactional
        def apply(tx):
            snapshot = ref.get(transaction=tx)
            if not snapshot.exists:
                raise CenterNotFound("Centro no encontrado")
            before = DistributionCenter.model_validate(snapshot.to_dict())
            if not before.active:
                raise CenterConflict("Centro inactivo: no se puede editar")
            if before.version != payload.expected_version:
                raise CenterConflict("La sede cambio: actualiza la lista")
            if before.code != payload.code.upper():
                raise CenterConflict("Codigo fijo: no se permite cambiarlo")
            after = before.model_copy(update={
                "name": payload.name, "address_label": payload.address_label,
                "geo": payload.geo, "location_precision": payload.location_precision,
                "version": before.version + 1, "updated_at": datetime.now(timezone.utc),
            })
            tx.update(ref, {
                "name": after.name, "address_label": after.address_label,
                "geo": after.geo.model_dump(mode="python"),
                "location_precision": after.location_precision,
                "version": after.version, "updated_at": after.updated_at,
            })
            return after
        return apply(self.db.transaction())

    def deactivate(self, center_id: str, *, expected_version: int) -> DistributionCenter:
        self._ref_id(center_id)
        ref = self.db.collection("distribution_centers").document(center_id)
        @firestore.transactional
        def apply(tx):
            snap = ref.get(transaction=tx)
            if not snap.exists:
                raise CenterNotFound("Centro no encontrado")
            before = DistributionCenter.model_validate(snap.to_dict())
            if not before.active:
                raise CenterConflict("Centro ya inactivo")
            if before.version != expected_version:
                raise CenterConflict("La sede cambio: actualiza la lista")
            after = before.model_copy(update={
                "active": False, "version": before.version + 1,
                "updated_at": datetime.now(timezone.utc),
            })
            tx.update(ref, {"active": False, "version": after.version, "updated_at": after.updated_at})
            return after
        return apply(self.db.transaction())
