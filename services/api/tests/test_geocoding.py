"""Autocomplete validates bounds, precision and provider failure without network."""
import httpx
import pytest
from fastapi import HTTPException
from app.geocoding import lookup_addresses


def test_missing_key(monkeypatch):
    monkeypatch.delenv("GEOAPIFY_API_KEY", raising=False)
    with pytest.raises(HTTPException) as e:
        lookup_addresses("Arequipa")
    assert e.value.status_code == 503


def test_too_short_query_rejected():
    with pytest.raises(HTTPException) as e:
        lookup_addresses("a", api_key="dummy")
    assert e.value.status_code == 422


def test_filters_out_of_area_and_flags_imprecise(monkeypatch):
    body = {"results": [
        {"place_id":"one","formatted":"Av. Ejemplo 22, Lima","lat":-12.08,"lon":-77.04,"housenumber":"22","result_type":"building"},
        {"place_id":"two","formatted":"Parque Ejemplo, Lima","lat":-12.1,"lon":-77.05,"result_type":"street"},
        {"place_id":"three","formatted":"Fuera Lima","lat":-13.0,"lon":-77.0,"result_type":"building"},
    ]}
    class Response:
        def raise_for_status(self): pass
        def json(self): return body
    class Client:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *_): pass
        def get(self, url, **kwargs):
            assert kwargs["params"]["filter"].startswith("rect:")
            assert kwargs["params"]["limit"] == 5
            return Response()
    monkeypatch.setattr(httpx, "Client", Client)
    items = lookup_addresses("Avenida Ejemplo", api_key="dummy").items
    assert len(items) == 2
    assert items[0].precision == "precise"
    assert items[1].precision == "approximate"
    assert items[1].warning


def test_provider_error_safe(monkeypatch):
    class Client:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *_): pass
        def get(self, url, **kwargs):
            raise httpx.TimeoutException("unavailable")
    monkeypatch.setattr(httpx, "Client", Client)
    with pytest.raises(HTTPException) as e:
        lookup_addresses("Av Arequipa", api_key="dummy")
    assert e.value.status_code == 503
