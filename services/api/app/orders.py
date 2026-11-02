"""US-003/US-004: validated orders and Firestore repository port."""
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol
from uuid import uuid4
from pydantic import BaseModel, Field, ConfigDict

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"

class Geo(BaseModel):
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)

class OrderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    address_label: str = Field(min_length=3, max_length=200)
    geo: Geo
    due_at: datetime | None = None

class Order(BaseModel):
    id: str
    created_by: str
    address_label: str
    geo: Geo
    status: OrderStatus
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime
    version: int
    data_origin: str = "synthetic"
    route_id: str | None = None

class OrderPage(BaseModel):
    items: list[Order]
    next_cursor: str | None = None

class OrderRepository(Protocol):
    def create(self, order: Order) -> None: ...
    def list(self, *, limit: int, after: str | None) -> OrderPage: ...

def new_order(payload: OrderCreate, *, actor_uid: str) -> Order:
    now = datetime.now(timezone.utc)
    return Order(
        id=str(uuid4()), created_by=actor_uid, address_label=payload.address_label,
        geo=payload.geo, status=OrderStatus.PENDING, due_at=payload.due_at,
        created_at=now, updated_at=now, version=1,
        data_origin="synthetic", route_id=None,
    )
