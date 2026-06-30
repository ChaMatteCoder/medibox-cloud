from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Medication


class MedicationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, medication: Medication) -> Medication:
        self.db.add(medication)
        self.db.commit()
        self.db.refresh(medication)
        return medication

    def list(self, patient_id: str | None = None) -> list[Medication]:
        statement = select(Medication).order_by(Medication.created_at.desc())
        if patient_id:
            statement = statement.where(Medication.patient_id == patient_id)
        return list(self.db.scalars(statement).all())

    def get(self, medication_id: str) -> Medication | None:
        return self.db.get(Medication, medication_id)
