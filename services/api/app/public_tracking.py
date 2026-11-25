"""US-016: opt-in order-scoped public tracking. Never log raw link tokens."""
import hashlib
import os
import re
import secrets
from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, ConfigDict, Field
from .firestore_config import firestore_client

TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{32,256}$")
ORDER_PATTERN = re.compile(r"^[0-9a-fA-F-]{36}$")
LINK_TTL = timedelta(hours=24)
COLLECTION = "public_tracking_links"


class LinkUnavailable(Exception):
    """Missing, revoked, expired, mismatched or invalid tracking link."""


class TrackingDisabled(Exception):
    """The opt-in tracking rollout gate is closed."""


def enabled():
    return os.environ.get("SMARTROUTE_PUBLIC_TRACKING_ENABLED") == "true"


def require_enabled():
    if not enabled():
        raise TrackingDisabled()


def token_hash(token: str) -> str:
    if not isinstance(token, str) or TOKEN_PATTERN.fullmatch(token) is None:
        raise LinkUnavailable()
    return hashlib.sha256(token.encode("ascii")).hexdigest()


class TokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str = Field(min_length=32, max_length=256, pattern=r"^[A-Za-z0-9_-]+$")


class TrackingView(BaseModel):
    order_reference: str
    status: str
    eta_minutes: int | None = None


class TrackingLink(BaseModel):
    token: str
    expires_at: datetime


class FirestorePublicTrackingRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else firestore_client()

    def issue(self, order_id: str) -> TrackingLink:
        require_enabled()
        if not ORDER_PATTERN.fullmatch(order_id):
            raise LinkUnavailable()
        order_snap = self.db.collection("orders").document(order_id).get()
        if not order_snap.exists:
            raise LinkUnavailable()
        order = order_snap.to_dict() or {}
        # Pilot policy: publish only synthetic orders.
        if order.get("data_origin") != "synthetic":
            raise LinkUnavailable()
        token = secrets.token_urlsafe(32)
        key = token_hash(token)
        expires = datetime.now(timezone.utc) + LINK_TTL
        self.db.collection(COLLECTION).document(key).create({
            "order_id": order_id, "expires_at": expires,
            "revoked": False, "created_at": datetime.now(timezone.utc),
        })
        # The token exists only in this single response, never persisted in cleartext.
        return TrackingLink(token=token, expires_at=expires)

    def resolve(self, token: str) -> TrackingView:
        require_enabled()
        key = token_hash(token)
        snap = self.db.collection(COLLECTION).document(key).get()
        if not snap.exists:
            raise LinkUnavailable()
        record = snap.to_dict() or {}
        expires = record.get("expires_at")
        order_id = record.get("order_id")
        now = datetime.now(timezone.utc)
        if (record.get("revoked") is not False
            or not isinstance(expires, datetime)
            or expires.tzinfo is None or expires <= now
            or not isinstance(order_id, str)
            or ORDER_PATTERN.fullmatch(order_id) is None):
            raise LinkUnavailable()
        order_snap = self.db.collection("orders").document(order_id).get()
        if not order_snap.exists:
            raise LinkUnavailable()
        order = order_snap.to_dict() or {}
        if order.get("id", order_id) != order_id or order.get("data_origin") != "synthetic":
            raise LinkUnavailable()
        status = order.get("status")
        if status not in {"PENDING", "ASSIGNED", "IN_TRANSIT", "DELIVERED", "FAILED"}:
            raise LinkUnavailable()
        # Public response intentionally excludes destination address, driver, GPS and route.
        return TrackingView(order_reference=order_id, status=status, eta_minutes=None)

    def revoke(self, token: str):
        require_enabled()
        key = token_hash(token)
        ref = self.db.collection(COLLECTION).document(key)
        if not ref.get().exists:
            raise LinkUnavailable()
        ref.update({"revoked": True})
