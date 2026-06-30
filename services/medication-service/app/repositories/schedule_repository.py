from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Medication, MedicationSchedule


class ScheduleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, schedule: MedicationSchedule) -> MedicationSchedule:
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        return schedule

    def list_by_patient(self, patient_id: str) -> list[MedicationSchedule]:
        statement = (
            select(MedicationSchedule)
            .join(Medication)
            .where(Medication.patient_id == patient_id)
            .order_by(MedicationSchedule.scheduled_time.asc())
        )
        return list(self.db.scalars(statement).all())
