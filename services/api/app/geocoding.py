"""Operator-only address search for the synthetic Lima pilot.

Geoapify API key is server side. No coordinates are inferred by the UI.
No persistent storage, and only 5 autocomplete matches are returned.
"""
import os
from typing import Literal

import httpx
from fastapi import HTTPException
from pydantic import BaseModel, Field


class AddressSuggestion(BaseModel):
    id: str
    label: str
    latitude: float
    longitude: float
    precision: Literal["precise", "approximate"]
    warning: str | None = None


class AddressSuggestions(BaseModel):
    items: list[AddressSuggestion] = Field(default_factory=list)
    source: str = "geoapify"
    notice: str | None = None


def lookup_addresses(text: str, *, api_key: str | None = None) -> AddressSuggestions:
    query = text.strip()
    if len(query) < 3 or len(query) > 120:
        raise HTTPException(422, "Escribe entre 3 y 120 caracteres para buscar")
    key = api_key or os.getenv("GEOAPIFY_API_KEY")
    if not key:
        raise HTTPException(503, "Servicio de búsqueda de direcciones no configurado")
    try:
        with httpx.Client(timeout=7.0) as client:
            response = client.get(
                "https://api.geoapify.com/v1/geocode/autocomplete",
                params={
                    "text": query, "format": "json", "lang": "es", "limit": 5,
                    "filter": "rect:-77.20,-12.30,-76.80,-11.80",
                    "bias": "proximity:-77.035,-12.095",
                    "apiKey": key,
                },
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError):
        raise HTTPException(503, "El buscador de direcciones no responde") from None
    items = []
    for x in data.get("results", [])[:5]:
        if not isinstance(x, dict):
            continue
        lat, lon = x.get("lat"), x.get("lon")
        if (not isinstance(lat, (int, float)) or isinstance(lat, bool)
            or not isinstance(lon, (int, float)) or isinstance(lon, bool)):
            continue
        if not (-12.30 <= lat <= -11.80 and -77.20 <= lon <= -76.80):
            continue
        label = str(x.get("formatted") or x.get("address_line1") or "").strip()[:200]
        if not label:
            continue
        has_number = bool(x.get("housenumber"))
        precision = "precise" if has_number and x.get("result_type") == "building" else "approximate"
        identifier = str(x.get("place_id") or f"{lat:.6f},{lon:.6f}")[:128]
        items.append(AddressSuggestion(
            id=identifier, label=label, latitude=lat, longitude=lon,
            precision=precision,
            warning=None if precision == "precise" else "Ubicación aproximada: confirma el punto en el mapa antes de guardar",
        ))
    return AddressSuggestions(items=items, notice=None if items else "No encontramos coincidencias válidas en el área piloto. Prueba otra referencia.")
