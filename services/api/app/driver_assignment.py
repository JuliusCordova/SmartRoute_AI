"""US-011 transport contracts for operator assignment and driver-owned route reads.

No persistence or privileged side-effects in this module. See SDD US-011.
"""
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator
from .orders import Geo


class DriverSummary(BaseModel):
    uid: str = Field(min_length=1, max_length=128)
    display_name: str = Field(min_length=1, max_length=120)
    active: bool
    available: bool


class DriverPage(BaseModel):
    items: list[DriverSummary]
    next_cursor: str | None = None


class AssignDriverRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    driver_id: str = Field(min_length=1, max_length=128)
    expected_version: int = Field(ge=1)
    idempotency_key: UUID

    @model_validator(mode="after")
    def check_driver_id(self):
        if "/" in self.driver_id or self.driver_id in (".", ".."):
            raise ValueError("Invalid driver ID")
        return self


class DriverStop(BaseModel):
    sequence: int = Field(ge=1)
    order_id: str = Field(min_length=1, max_length=128)
    address_label: str
    geo: Geo
    status: Literal["ASSIGNED", "IN_TRANSIT", "DELIVERED", "FAILED"] = "ASSIGNED"


class DriverRoute(BaseModel):
    """Safe projection; only returned for the Firebase UID of the caller."""
    id: str
    status: Literal["PLANNED", "ACTIVE", "COMPLETED"]
    version: int = Field(ge=1)
    depot: Geo
    stops: list[DriverStop] = Field(min_length=1, max_length=10)
    optimized_seconds: int = Field(ge=0)
    optimized_meters: int = Field(ge=0)
    data_origin: Literal["estimated"] = "estimated"
    assigned_at: datetime | None = None
    started_at: datetime | None = None
