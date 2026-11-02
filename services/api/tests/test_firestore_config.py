"""No GCP I/O. A missing or shared database is a configuration error."""
import pytest
from app.firestore_config import database_id


def test_missing_database_fails_closed(monkeypatch):
    monkeypatch.delenv("FIRESTORE_EMULATOR_HOST", raising=False)
    monkeypatch.delenv("FIRESTORE_DATABASE_ID", raising=False)
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "proyectopersonal-480420")
    with pytest.raises(RuntimeError, match="required"):
        database_id()


@pytest.mark.parametrize("blocked", ["(default)", "gestioncitas"])
def test_existing_databases_are_protected(monkeypatch, blocked):
    monkeypatch.delenv("FIRESTORE_EMULATOR_HOST", raising=False)
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "proyectopersonal-480420")
    monkeypatch.setenv("FIRESTORE_DATABASE_ID", blocked)
    with pytest.raises(RuntimeError, match="Protected"):
        database_id()


def test_named_db_allowed_for_approved_project(monkeypatch):
    monkeypatch.delenv("FIRESTORE_EMULATOR_HOST", raising=False)
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "proyectopersonal-480420")
    monkeypatch.setenv("FIRESTORE_DATABASE_ID", "smartroute")
    assert database_id() == "smartroute"


def test_other_named_db_rejected_in_approved_project(monkeypatch):
    monkeypatch.delenv("FIRESTORE_EMULATOR_HOST", raising=False)
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "proyectopersonal-480420")
    monkeypatch.setenv("FIRESTORE_DATABASE_ID", "other")
    with pytest.raises(RuntimeError, match="dedicated"):
        database_id()


def test_emulator_keeps_default_for_legacy_test_fixtures(monkeypatch):
    monkeypatch.setenv("FIRESTORE_EMULATOR_HOST", "127.0.0.1:8085")
    monkeypatch.delenv("FIRESTORE_DATABASE_ID", raising=False)
    assert database_id() == "(default)"
