from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field, field_validator

VALID_WEEKDAYS = {"MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"}


class ScheduleCreate(BaseModel):
    medication_id: str = Field(max_length=36)
    scheduled_time: time
    weekdays: list[str] = Field(min_length=1, max_length=7)

    @field_validator("weekdays")
    @classmethod
    def normalize_weekdays(cls, value: list[str]) -> list[str]:
        weekdays = [item.upper() for item in value]
        invalid = set(weekdays) - VALID_WEEKDAYS
        if invalid:
            raise ValueError("Weekdays must use MON, TUE, WED, THU, FRI, SAT or SUN")
        return weekdays


class ScheduleRead(BaseModel):
    id: str
    medication_id: str
    scheduled_time: time
    weekdays: list[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
