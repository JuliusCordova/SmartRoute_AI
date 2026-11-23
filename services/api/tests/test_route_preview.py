"""Preview validation and deterministic solver tests without network or API keys."""
import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from app.route_preview import PreviewRequest, compute_preview


def request():
    return PreviewRequest.model_validate({"depot":{"id":"D","latitude":-12.095,"longitude":-77.035},
        "stops":[{"id":"A","latitude":-12.1,"longitude":-77.04},{"id":"B","latitude":-12.11,"longitude":-77.05}]})


def test_requires_provider_key(monkeypatch):
    monkeypatch.delenv("ORS_API_KEY", raising=False)
    with pytest.raises(HTTPException) as error:
        compute_preview(request())
    assert error.value.status_code == 503


def test_rejects_duplicate_ids():
    payload = request().model_dump()
    payload["stops"][1]["id"] = "A"
    with pytest.raises(ValidationError):
        PreviewRequest.model_validate(payload)


def test_rejects_coordinates_outside_pilot():
    payload = request().model_dump()
    payload["stops"][1]["latitude"] = 15
    with pytest.raises(ValidationError):
        PreviewRequest.model_validate(payload)


def test_optimized_uses_road_matrix(monkeypatch):
    matrix = {"durations": [[0, 30, 20], [30, 0, 100], [20, 5, 0]],
              "distances": [[0, 300, 200], [300, 0, 1000], [200, 50, 0]]}
    class Resp:
        def raise_for_status(self): pass
        def json(self): return matrix
    class Client:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *_): pass
        def post(self, url, **kwargs):
            if "matrix" in url: return Resp()
            raise httpx.ConnectError("geometry unavailable")
    import httpx
    monkeypatch.setattr(httpx, "Client", Client)
    result = compute_preview(request(), api_key="test")
    assert sorted(result.ordered_order_ids) == ["A", "B"]
    assert result.data_origin == "estimated"
    assert result.optimized_seconds <= result.baseline_seconds
    assert result.route_geometry is None
    # DEF-01: the improvement is based on exact seconds, not rounded display minutes.
    # Baseline D→A→B→D: 30+100+20=150 seconds.
    # Optimized D→B→A→D: 20+5+30=55 seconds.
    assert result.baseline_seconds == 150
    assert result.optimized_seconds == 55
    assert result.improvement_pct == 63.33
    assert result.ordered_order_ids == ["B", "A"]

