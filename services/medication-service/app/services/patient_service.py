from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Patient
from app.repositories.patient_repository import PatientRepository
from app.schemas.patient import PatientCreate


class PatientService:
    def __init__(self, db: Session) -> None:
        self.repository = PatientRepository(db)

    def create(self, payload: PatientCreate, caregiver_id: str) -> Patient:
        patient = Patient(
            name=payload.name,
            birth_date=payload.birth_date,
            caregiver_id=payload.caregiver_id or caregiver_id,
        )
        return self.repository.create(patient)

    def list(self) -> list[Patient]:
        return self.repository.list()

    def get(self, patient_id: str) -> Patient:
        patient = self.repository.get(patient_id)
        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )
        return patient
