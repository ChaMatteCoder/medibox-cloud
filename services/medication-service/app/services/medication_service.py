from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Medication
from app.repositories.medication_repository import MedicationRepository
from app.repositories.patient_repository import PatientRepository
from app.schemas.medication import MedicationCreate


class MedicationService:
    def __init__(self, db: Session) -> None:
        self.repository = MedicationRepository(db)
        self.patient_repository = PatientRepository(db)

    def create(self, payload: MedicationCreate) -> Medication:
        if self.patient_repository.get(payload.patient_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )

        medication = Medication(
            patient_id=payload.patient_id,
            name=payload.name,
            dosage=payload.dosage,
            instructions=payload.instructions,
            active=payload.active,
        )
        return self.repository.create(medication)

    def list_all(self, patient_id: str | None = None) -> list[Medication]:
        return self.repository.list_all(patient_id=patient_id)

    def get(self, medication_id: str) -> Medication:
        medication = self.repository.get(medication_id)
        if medication is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found",
            )
        return medication
