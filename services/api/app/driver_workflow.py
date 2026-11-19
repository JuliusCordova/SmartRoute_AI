"""US-012/013/014: contratos del ciclo de ejecución del conductor.

El Firebase UID se obtiene de require_driver; nunca se acepta del cliente.
Los UUID permiten reintentos seguros y expected_version evita escrituras obsoletas.
"""
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator


class WorkflowRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)
    idempotency_key: UUID


class StopResultRequest(WorkflowRequest):
    reason: str | None = Field(default=None, max_length=250)

    @model_validator(mode="after")
    def validate_reason(self):
        if self.reason is not None:
            self.reason = self.reason.strip()
            if not self.reason:
                raise ValueError("Empty reason")
        return self


class RouteReceipt(BaseModel):
    id: str
    status: Literal["ACTIVE", "COMPLETED"]
    version: int = Field(ge=1)


class StopReceipt(RouteReceipt):
    order_id: str
    order_status: Literal["DELIVERED", "FAILED"]
