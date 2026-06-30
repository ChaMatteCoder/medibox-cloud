from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import MedicationSchedule
from app.schemas.schedule import ScheduleCreate, ScheduleRead
from app.services.schedule_service import ScheduleService

router = APIRouter()


@router.post("", response_model=ScheduleRead, status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreate,
    _: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MedicationSchedule:
    return ScheduleService(db).create(payload)


@router.get("/patient/{patient_id}", response_model=list[ScheduleRead])
def list_schedules_by_patient(
    patient_id: str,
    _: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MedicationSchedule]:
    return ScheduleService(db).list_by_patient(patient_id)
