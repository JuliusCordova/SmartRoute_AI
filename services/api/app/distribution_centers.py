"""US-017: master data for operator-managed distribution centers."""
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from .orders import Geo


class CenterCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    code: str = Field(min_length=2, max_length=24, pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
    name: str = Field(min_length=3, max_length=80)
    address_label: str = Field(min_length=3, max_length=200)
    geo: Geo
    location_precision: Literal["precise", "approximate"]
    approximate_confirmed: bool = False

    def ensure_valid(self):
        if not (-12.30 <= self.geo.latitude <= -11.80 and -77.20 <= self.geo.longitude <= -76.80):
            raise ValueError("Centro fuera del area piloto Lima")
        if self.location_precision == "approximate" and not self.approximate_confirmed:
            raise ValueError("Se requiere confirmar la ubicacion aproximada")


class CenterUpdate(CenterCreate):
    expected_version: int = Field(ge=1)


class CenterDeactivate(BaseModel):
    expected_version: int = Field(ge=1)


class DistributionCenter(BaseModel):
    id: str
    code: str
    name: str
    address_label: str
    geo: Geo
    location_precision: Literal["precise", "approximate"]
    active: bool = True
    version: int = 1
    created_at: datetime
    updated_at: datetime
    created_by: str


class CenterPage(BaseModel):
    items: list[DistributionCenter]
    next_cursor: str | None = None


class CenterNotFound(Exception):
    pass


class CenterConflict(Exception):
    pass


def create_center(payload: CenterCreate, actor_uid: str) -> DistributionCenter:
    payload.ensure_valid()
    now = datetime.now(timezone.utc)
    return DistributionCenter(
        id=str(uuid4()), code=payload.code.upper(), name=payload.name,
        address_label=payload.address_label, geo=payload.geo,
        location_precision=payload.location_precision, created_by=actor_uid,
        created_at=now, updated_at=now,
    )
