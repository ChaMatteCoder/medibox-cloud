from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MedicationCreate(BaseModel):
    patient_id: str = Field(max_length=36)
    name: str = Field(min_length=2, max_length=120)
    dosage: str = Field(min_length=1, max_length=120)
    instructions: str | None = None
    active: bool = True


class MedicationRead(BaseModel):
    id: str
    patient_id: str
    name: str
    dosage: str
    instructions: str | None
    active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
