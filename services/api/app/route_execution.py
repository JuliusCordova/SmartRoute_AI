"""US-012 transport contracts: owner-scoped route execution."""
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StartRouteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)
    idempotency_key: UUID


class RouteExecutionResult(BaseModel):
    id: str
    driver_id: str
    status: Literal["ACTIVE"]
    version: int = Field(ge=2)
    started_at: datetime


class RouteExecutionMissing(Exception):
    """Driver has no assigned route."""


class RouteExecutionConflict(Exception):
    """Route, ownership, identity, version or reservation invalid."""
