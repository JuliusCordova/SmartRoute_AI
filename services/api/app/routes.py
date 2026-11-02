"""US-005: routes and bounded assignment contract."""
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field
from .orders import Geo

class RouteStatus(str, Enum):
    DRAFT = "DRAFT"
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class RouteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    driver_id: str = Field(min_length=1, max_length=128)
    depot: Geo

class Route(BaseModel):
    id: str
    driver_id: str
    depot: Geo
    status: RouteStatus
    order_ids: list[str] = Field(default_factory=list)
    version: int = 1
    created_at: datetime

class OrderAssignment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    order_ids: list[str] = Field(min_length=1, max_length=10)

class AssignmentConflict(Exception):
    """Order was already assigned, route is not draft or capacity exceeded."""

class RecordMissing(Exception):
    """Route, driver or order does not exist."""

def new_route(payload: RouteCreate) -> Route:
    return Route(id=str(uuid4()), driver_id=payload.driver_id,
                 depot=payload.depot, status=RouteStatus.DRAFT,
                 created_at=datetime.now(timezone.utc))
