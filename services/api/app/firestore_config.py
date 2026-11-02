"""Fail-closed Firestore database selection for a shared GCP project.

Never silently select (default) in deployed code. Emulator tests may use default.
No cloud access at import time.
"""
import os
from functools import lru_cache

APPROVED_PROJECT = "proyectopersonal-480420"
SMARTROUTE_DB = "smartroute"


def database_id() -> str:
    selected = os.environ.get("FIRESTORE_DATABASE_ID", "").strip()
    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT") or ""
    emulator = bool(os.environ.get("FIRESTORE_EMULATOR_HOST"))

    if emulator:
        return selected or "(default)"

    if not selected:
        raise RuntimeError("FIRESTORE_DATABASE_ID is required outside the emulator")
    if selected in ("(default)", "gestioncitas"):
        raise RuntimeError("Protected Firestore database: SmartRoute cannot use shared databases")
    if project == APPROVED_PROJECT and selected != SMARTROUTE_DB:
        raise RuntimeError("SmartRoute requires dedicated Firestore database 'smartroute'")
    return selected


@lru_cache(maxsize=1)
def firestore_client():
    from google.cloud import firestore
    return firestore.Client(
        project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
        database=database_id(),
    )
