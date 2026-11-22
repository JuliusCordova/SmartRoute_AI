"""US-010 contract: persist a server-recomputed optimized route, never client metrics."""
from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator
from .orders import Geo


class OptimizedRouteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    depot: Geo
    distribution_center_id: str | None = Field(default=None, min_length=1, max_length=128)
    order_ids: list[str] = Field(min_length=1, max_length=10)
    idempotency_key: UUID

    @model_validator(mode="after")
    def check_unique_orders(self):
        if len(set(self.order_ids)) != len(self.order_ids):
            raise ValueError("Duplicate order IDs")
        if any(not x or len(x) > 128 or "/" in x for x in self.order_ids):
            raise ValueError("Invalid order ID")
        return self


class OptimizedRoute(BaseModel):
    id: str
    route_type: Literal["OPTIMIZED"] = "OPTIMIZED"
    status: Literal["PLANNED", "ACTIVE", "COMPLETED", "CANCELLED"] = "PLANNED"
    driver_id: str | None = None
    assigned_by: str | None = None
    assigned_at: datetime | None = None
    created_by: str
    depot: Geo
    distribution_center_id: str | None = None
    distribution_center_name: str | None = None
    order_ids: list[str]
    baseline_order_ids: list[str]
    ordered_order_ids: list[str]
    baseline_seconds: int = Field(ge=0)
    optimized_seconds: int = Field(ge=0)
    baseline_meters: int = Field(ge=0)
    optimized_meters: int = Field(ge=0)
    improvement_pct: float = Field(ge=0, le=100)
    matrix_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    matrix_provider: Literal["openrouteservice"] = "openrouteservice"
    data_origin: Literal["estimated"] = "estimated"
    warnings: list[str] = Field(default_factory=list)
    version: int = 1
    created_at: datetime
    updated_at: datetime


class OptimizedRoutePage(BaseModel):
    items: list[OptimizedRoute]
    next_cursor: str | None = None


class OptimizedRouteConflict(Exception):
    """Concurrent update, duplicate booking, or idempotency key collision."""


class OptimizedRouteMissing(Exception):
    """Requested order or route is missing."""


class PersistedStop(BaseModel):
    id: str
    address_label: str
    geo: Geo
    sequence: int = Field(ge=1)


class OptimizedRouteDetail(OptimizedRoute):
    """Read model; the stored order and metrics are never recomputed."""
    stops: list[PersistedStop] = Field(default_factory=list)
    route_geometry: list[list[float]] | None = None
    geometry_origin: Literal["openrouteservice", "schematic"] = "schematic"
    detail_warnings: list[str] = Field(default_factory=list)
