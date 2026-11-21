"""US-011 validation-only contract tests; no network or Firestore mutations."""
from uuid import uuid4
import pytest
from pydantic import ValidationError
from app.driver_assignment import AssignDriverRequest, DriverRoute, DriverSummary


def test_assignment_contract_requires_firebase_uid_version_and_idempotency():
    key = uuid4()
    request = AssignDriverRequest.model_validate({
        "driver_id": "synthetic-driver-001", "expected_version": 1,
        "idempotency_key": str(key),
    })
    assert request.driver_id == "synthetic-driver-001"
    assert request.expected_version == 1
    assert request.idempotency_key == key


@pytest.mark.parametrize("patch", [
    {"driver_id": ""},
    {"driver_id": "../other"},
    {"driver_id": "users/another"},
    {"expected_version": 0},
    {"idempotency_key": "not-a-uuid"},
    {"extra": "forbidden"},
])
def test_assignment_invalid_payload_rejected(patch):
    payload = {"driver_id": "synthetic-driver-001", "expected_version": 1,
               "idempotency_key": str(uuid4())}
    payload.update(patch)
    with pytest.raises(ValidationError):
        AssignDriverRequest.model_validate(payload)


def test_driver_route_contains_ordered_stops_without_other_drivers():
    route = DriverRoute.model_validate({
        "id": str(uuid4()), "status": "PLANNED", "version": 2,
        "depot": {"latitude": -12.095, "longitude": -77.035},
        "stops": [{
            "sequence": 1, "order_id": "synthetic-order-01",
            "address_label": "Dirección ficticia, Lima",
            "geo": {"latitude": -12.10, "longitude": -77.04},
        }],
        "optimized_seconds": 1500, "optimized_meters": 15260,
    })
    assert route.version == 2
    assert route.stops[0].sequence == 1
    assert "driver_id" not in route.model_dump()
    assert route.data_origin == "estimated"


def test_driver_profile_requires_explicit_active_and_available():
    candidate = DriverSummary(
        uid="synthetic-driver-001", display_name="Conductor de prueba",
        active=True, available=True,
    )
    assert candidate.active and candidate.available
    with pytest.raises(ValidationError):
        DriverSummary(uid="synthetic-driver-001", display_name="Conductor de prueba", active=True)
