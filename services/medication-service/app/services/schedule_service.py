from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import MedicationSchedule
from app.repositories.medication_repository import MedicationRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.schedule import ScheduleCreate


class ScheduleService:
    def __init__(self, db: Session) -> None:
        self.repository = ScheduleRepository(db)
        self.medication_repository = MedicationRepository(db)
        self.patient_repository = PatientRepository(db)

    def create(self, payload: ScheduleCreate) -> MedicationSchedule:
        if self.medication_repository.get(payload.medication_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medication not found",
            )

        schedule = MedicationSchedule(
            medication_id=payload.medication_id,
            scheduled_time=payload.scheduled_time,
            weekdays=payload.weekdays,
        )
        return self.repository.create(schedule)

    def list_by_patient(self, patient_id: str) -> list[MedicationSchedule]:
        if self.patient_repository.get(patient_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found",
            )
        return self.repository.list_by_patient(patient_id)
