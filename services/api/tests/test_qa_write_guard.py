"""QA guard tests: pure configuration checks. Never contacts Firestore/GCP."""
import pytest

from app.qa_write_guard import QaWriteGuardDenied, enforce_qa_write_guard

UID = "qa-synthetic-driver"
ROUTE = "qa-synthetic-route"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for key in ("SMARTROUTE_QA_WRITE_GUARD", "SMARTROUTE_QA_DRIVER_UID",
                "SMARTROUTE_QA_ROUTE_ID", "APP_ENV",
                "GOOGLE_CLOUD_PROJECT", "FIRESTORE_DATABASE_ID",
                "FIRESTORE_EMULATOR_HOST"):
        monkeypatch.delenv(key, raising=False)


def setup_guard(monkeypatch):
    monkeypatch.setenv("SMARTROUTE_QA_WRITE_GUARD", "true")
    monkeypatch.setenv("SMARTROUTE_QA_DRIVER_UID", UID)
    monkeypatch.setenv("SMARTROUTE_QA_ROUTE_ID", ROUTE)
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "proyectopersonal-480420")
    monkeypatch.setenv("FIRESTORE_DATABASE_ID", "smartroute")


def test_without_explicit_guard_preserves_current_behavior():
    enforce_qa_write_guard(driver_uid="driver-A", route_id="route-A")


def test_exact_qa_driver_and_route_allowed(monkeypatch):
    setup_guard(monkeypatch)
    enforce_qa_write_guard(driver_uid=UID, route_id=ROUTE)


@pytest.mark.parametrize("uid,route", [
    ("manuel-synthetic-driver", ROUTE),
    (UID, "different-synthetic-route"),
    ("", ROUTE),
])
def test_other_driver_or_route_is_blocked(monkeypatch, uid, route):
    setup_guard(monkeypatch)
    with pytest.raises(QaWriteGuardDenied):
        enforce_qa_write_guard(driver_uid=uid, route_id=route)


@pytest.mark.parametrize("var,value", [
    ("APP_ENV", "production"),
    ("GOOGLE_CLOUD_PROJECT", "unapproved-project"),
    ("FIRESTORE_DATABASE_ID", "(default)"),
    ("FIRESTORE_DATABASE_ID", "gestioncitas"),
])
def test_rejects_wrong_environment_or_database(monkeypatch, var, value):
    setup_guard(monkeypatch)
    monkeypatch.setenv(var, value)
    with pytest.raises(QaWriteGuardDenied):
        enforce_qa_write_guard(driver_uid=UID, route_id=ROUTE)


def test_missing_qa_driver_fail_closed(monkeypatch):
    setup_guard(monkeypatch)
    monkeypatch.delenv("SMARTROUTE_QA_DRIVER_UID")
    with pytest.raises(QaWriteGuardDenied):
        enforce_qa_write_guard(driver_uid=UID, route_id=ROUTE)


def test_missing_qa_route_fail_closed(monkeypatch):
    setup_guard(monkeypatch)
    monkeypatch.delenv("SMARTROUTE_QA_ROUTE_ID")
    with pytest.raises(QaWriteGuardDenied):
        enforce_qa_write_guard(driver_uid=UID, route_id=ROUTE)


def test_invalid_boolean_fail_closed(monkeypatch):
    setup_guard(monkeypatch)
    monkeypatch.setenv("SMARTROUTE_QA_WRITE_GUARD", "false")
    with pytest.raises(QaWriteGuardDenied):
        enforce_qa_write_guard(driver_uid=UID, route_id=ROUTE)
