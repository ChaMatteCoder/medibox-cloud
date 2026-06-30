from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Medication
from app.schemas.medication import MedicationCreate, MedicationRead
from app.services.medication_service import MedicationService

router = APIRouter()


@router.post("", response_model=MedicationRead, status_code=status.HTTP_201_CREATED)
def create_medication(
    payload: MedicationCreate,
    _: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Medication:
    return MedicationService(db).create(payload)


@router.get("", response_model=list[MedicationRead])
def list_medications(
    patient_id: str | None = Query(default=None),
    _: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Medication]:
    return MedicationService(db).list_all(patient_id=patient_id)


@router.get("/{medication_id}", response_model=MedicationRead)
def get_medication(
    medication_id: str,
    _: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Medication:
    return MedicationService(db).get(medication_id)
