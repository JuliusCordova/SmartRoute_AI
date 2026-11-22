"""US-V1-008: GPS only for an active, consenting, assigned DRIVER."""
from datetime import datetime, timezone, timedelta
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class GPSFix(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route_id: str = Field(min_length=1, max_length=128)
    latitude: float = Field(ge=-12.30, le=-11.80, allow_inf_nan=False)
    longitude: float = Field(ge=-77.20, le=-76.80, allow_inf_nan=False)
    accuracy_m: float = Field(ge=0, le=500, allow_inf_nan=False)
    captured_at: datetime
    consent: Literal[True]

    @model_validator(mode="after")
    def ensure_fresh_utc(self):
        now = datetime.now(timezone.utc)
        if self.captured_at.tzinfo is None:
            raise ValueError("GPS timestamp needs timezone")
        if not now-timedelta(seconds=120) <= self.captured_at <= now+timedelta(seconds=30):
            raise ValueError("GPS timestamp is stale or in the future")
        return self


class GPSReceipt(BaseModel):
    route_id: str
    stored_at: datetime
    status: Literal["CURRENT"] = "CURRENT"


class LastGPS(BaseModel):
    route_id: str
    driver_id: str
    latitude: float
    longitude: float
    accuracy_m: float
    captured_at: datetime
    stored_at: datetime
    status: Literal["CURRENT", "STALE"]


class GPSDenied(Exception): pass
class GPSMissing(Exception): pass


def freshness(stored_at: datetime, now: datetime | None = None) -> str:
    moment = now or datetime.now(timezone.utc)
    return "STALE" if (moment-stored_at).total_seconds() > 120 else "CURRENT"
