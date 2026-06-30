from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.db.models import DeviceEvent
from app.messaging.rabbitmq import RabbitMQPublisher
from app.repositories.event_repository import EventRepository
from app.schemas.event import DeviceEventCreate

logger = logging.getLogger(__name__)


class EventService:
    def __init__(self, db: Session) -> None:
        self.repository = EventRepository(db)
        self.publisher = RabbitMQPublisher()

    def create(self, payload: DeviceEventCreate) -> DeviceEvent:
        event = DeviceEvent(
            patient_id=payload.patient_id,
            medication_id=payload.medication_id,
            event_type=payload.event_type.value,
            occurred_at=payload.occurred_at,
            payload=payload.payload,
        )
        event = self.repository.create(event)

        message = {
            "event_id": event.id,
            "patient_id": event.patient_id,
            "medication_id": event.medication_id,
            "event_type": event.event_type,
            "occurred_at": event.occurred_at.isoformat(),
        }
        try:
            self.publisher.publish_notification(message)
            logger.info("Published notification message for event %s", event.id)
        except Exception:
            logger.exception("Could not publish notification for event %s", event.id)

        return event

    def list(self) -> list[DeviceEvent]:
        return self.repository.list()

    def list_by_patient(self, patient_id: str) -> list[DeviceEvent]:
        return self.repository.list_by_patient(patient_id)
