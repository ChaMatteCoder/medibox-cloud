from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import DeviceEventType


class DeviceEventCreate(BaseModel):
    patient_id: str = Field(max_length=36)
    medication_id: str = Field(max_length=36)
    event_type: DeviceEventType
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)


class DeviceEventRead(BaseModel):
    id: str
    patient_id: str
    medication_id: str
    event_type: DeviceEventType
    occurred_at: datetime
    payload: dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
