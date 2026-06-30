from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import DeviceEvent


class EventRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, event: DeviceEvent) -> DeviceEvent:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_all(self) -> list[DeviceEvent]:
        statement = select(DeviceEvent).order_by(DeviceEvent.occurred_at.desc())
        return list(self.db.scalars(statement).all())

    def list_by_patient(self, patient_id: str) -> list[DeviceEvent]:
        statement = (
            select(DeviceEvent)
            .where(DeviceEvent.patient_id == patient_id)
            .order_by(DeviceEvent.occurred_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def count_by_patient(self, patient_id: str) -> list[DeviceEvent]:
        statement = select(DeviceEvent).where(DeviceEvent.patient_id == patient_id)
        return list(self.db.scalars(statement).all())
