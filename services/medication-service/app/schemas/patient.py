from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PatientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    birth_date: date
    caregiver_id: str | None = Field(default=None, max_length=36)


class PatientRead(BaseModel):
    id: str
    name: str
    birth_date: date
    caregiver_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
