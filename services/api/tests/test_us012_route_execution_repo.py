"""US-012 Firestore transaction tests without network access or credentials."""
from copy import deepcopy
from uuid import uuid4

import pytest
from app import firestore_route_execution as mod
from app.route_execution import StartRouteRequest, RouteExecutionConflict, RouteExecutionMissing

UID = "synthetic-driver"
RID = "synthetic-route"


class Snapshot:
    def __init__(self, value):
        self.exists = value is not None
        self.value = deepcopy(value)

    def to_dict(self):
        return deepcopy(self.value)


class Document:
    def __init__(self, store, collection, name):
        self.store = store
        self.key = (collection, name)

    def get(self, transaction=None):
        return Snapshot(self.store.get(self.key))


class Collection:
    def __init__(self, store, name):
        self.store, self.name = store, name

    def document(self, name):
        return Document(self.store, self.name, name)


class Tx:
    def __init__(self, store):
        self.store = store
        self.events = []

    def update(self, ref, changes):
        assert ref.key in self.store
        self.store[ref.key].update(changes)
        self.events.append(("update", ref.key))

    def create(self, ref, value):
        assert ref.key not in self.store
        self.store[ref.key] = value
        self.events.append(("create", ref.key))


class DB:
    def __init__(self, store):
        self.store = store
        self.tx = Tx(store)

    def collection(self, name):
        return Collection(self.store, name)

    def transaction(self):
        return self.tx


def seed():
    return {
        ("driver_assignments", UID): {
            "driver_id": UID, "route_id": RID, "status": "RESERVED", "version": 1,
        },
        ("routes", RID): {
            "id": RID, "route_type": "OPTIMIZED", "status": "PLANNED",
            "driver_id": UID, "version": 2,
        },
        ("users", UID): {"role": "DRIVER", "active": True},
        ("drivers", UID): {"uid": UID, "active": True},
    }


@pytest.fixture(autouse=True)
def fake_transactional(monkeypatch):
    # Firestore @transactional wraps the function at invocation time.
    monkeypatch.setattr(mod.firestore, "transactional", lambda fn: fn)
    monkeypatch.setattr(mod.firestore, "Increment", lambda n: n)


def payload(key=None, version=2):
    return StartRouteRequest(
        expected_version=version, idempotency_key=key or uuid4())


def test_start_is_atomic_from_driver_reservation_and_retries_do_not_mutate():
    db = DB(seed())
    repo = mod.FirestoreRouteExecutionRepository(db)
    p = payload()
    started = repo.start(driver_uid=UID, payload=p)
    assert started.status == "ACTIVE"
    assert started.version == 3
    assert db.store[("routes", RID)]["started_by"] == UID
    assert db.store[("routes", RID)]["status"] == "ACTIVE"
    assert db.store[("driver_assignments", UID)]["status"] == "ACTIVE"
    assert sum(key[0] == "route_events" for key in db.store) == 1
    before_events = len(db.tx.events)
    retry = repo.start(driver_uid=UID, payload=p)
    assert retry == started
    assert len(db.tx.events) == before_events
    with pytest.raises(RouteExecutionConflict):
        repo.start(driver_uid=UID, payload=payload(p.idempotency_key, version=3))


@pytest.mark.parametrize("change", [
    lambda s: s[("routes", RID)].update(version=99),
    lambda s: s[("routes", RID)].update(driver_id="other"),
    lambda s: s[("routes", RID)].update(status="COMPLETED"),
    lambda s: s[("driver_assignments", UID)].update(route_id="another"),
    lambda s: s[("drivers", UID)].update(active=False),
    lambda s: s[("users", UID)].update(role="OPERATOR"),
])
def test_inconsistent_state_never_writes(change):
    store = seed()
    change(store)
    db = DB(store)
    with pytest.raises(RouteExecutionConflict):
        mod.FirestoreRouteExecutionRepository(db).start(driver_uid=UID, payload=payload())
    assert not db.tx.events


def test_missing_driver_reservation_is_not_a_new_route():
    store = seed()
    del store[("driver_assignments", UID)]
    db = DB(store)
    with pytest.raises(RouteExecutionMissing):
        mod.FirestoreRouteExecutionRepository(db).start(driver_uid=UID, payload=payload())
    assert not db.tx.events
