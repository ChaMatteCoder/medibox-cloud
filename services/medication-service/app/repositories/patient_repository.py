from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Patient


class PatientRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, patient: Patient) -> Patient:
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def list_all(self) -> list[Patient]:
        statement = select(Patient).order_by(Patient.created_at.desc())
        return list(self.db.scalars(statement).all())

    def get(self, patient_id: str) -> Patient | None:
        return self.db.get(Patient, patient_id)
