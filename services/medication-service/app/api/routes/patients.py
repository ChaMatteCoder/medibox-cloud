from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Patient
from app.schemas.patient import PatientCreate, PatientRead
from app.services.patient_service import PatientService

router = APIRouter()


@router.post("", response_model=PatientRead, status_code=status.HTTP_201_CREATED)
def create_patient(
    payload: PatientCreate,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Patient:
    return PatientService(db).create(payload, caregiver_id=current_user["sub"])


@router.get("", response_model=list[PatientRead])
def list_patients(
    _: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Patient]:
    return PatientService(db).list()


@router.get("/{patient_id}", response_model=PatientRead)
def get_patient(
    patient_id: str,
    _: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Patient:
    return PatientService(db).get(patient_id)
