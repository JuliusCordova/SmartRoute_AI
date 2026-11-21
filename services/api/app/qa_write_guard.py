"""Optional US-014 tagged-revision write guard, fail-closed when configured.

This controls only driver workflow writes, not driver GET/read endpoints.
It is an additional restriction alongside Firebase + Firestore ownership checks,
NOT a replacement for those checks. Set only on an isolated 0%-traffic revision.
"""
import os

from .firestore_config import APPROVED_PROJECT, SMARTROUTE_DB


class QaWriteGuardDenied(Exception):
    """The QA-only write restriction rejects this mutation."""


def enforce_qa_write_guard(*, driver_uid: str, route_id: str) -> None:
    mode = os.environ.get("SMARTROUTE_QA_WRITE_GUARD")
    if mode is None:
        return  # Existing production/staging behavior remains unchanged.
    if mode != "true":
        raise QaWriteGuardDenied("QA write guard misconfigured")

    # The emulator is allowed only for synthetic test fixtures, never for live QA.
    emulator = bool(os.environ.get("FIRESTORE_EMULATOR_HOST"))
    if not emulator and (
        os.environ.get("APP_ENV") != "staging"
        or os.environ.get("GOOGLE_CLOUD_PROJECT") != APPROVED_PROJECT
        or os.environ.get("FIRESTORE_DATABASE_ID") != SMARTROUTE_DB
    ):
        raise QaWriteGuardDenied("QA guard requires approved staging environment")

    expected_uid = os.environ.get("SMARTROUTE_QA_DRIVER_UID", "")
    expected_route = os.environ.get("SMARTROUTE_QA_ROUTE_ID", "")
    if not expected_uid or not expected_route or "/" in expected_uid or "/" in expected_route:
        raise QaWriteGuardDenied("QA guard identity or route missing")
    if driver_uid != expected_uid or route_id != expected_route:
        raise QaWriteGuardDenied("QA guard does not permit this driver or route")
