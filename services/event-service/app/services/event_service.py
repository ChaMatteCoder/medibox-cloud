import logging

from sqlalchemy.orm import Session

from app.db.models import DeviceEvent, DeviceEventType
from app.messaging.rabbitmq import RabbitMQPublisher
from app.repositories.event_repository import EventRepository
from app.schemas.event import AdherenceSummary, DeviceEventCreate

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

    def list_all(self) -> list[DeviceEvent]:
        return self.repository.list_all()

    def list_by_patient(self, patient_id: str) -> list[DeviceEvent]:
        return self.repository.list_by_patient(patient_id)

    def get_adherence_summary(self, patient_id: str) -> AdherenceSummary:
        events = self.repository.count_by_patient(patient_id)
        doses_taken = self._count_events(events, DeviceEventType.DOSE_TAKEN)
        doses_missed = self._count_events(events, DeviceEventType.DOSE_MISSED)
        doses_delayed = self._count_events(events, DeviceEventType.DOSE_DELAYED)
        dose_events = doses_taken + doses_missed + doses_delayed

        adherence_rate = 0.0
        if dose_events > 0:
            adherence_rate = round((doses_taken / dose_events) * 100, 2)

        return AdherenceSummary(
            total_events=len(events),
            doses_taken=doses_taken,
            doses_missed=doses_missed,
            doses_delayed=doses_delayed,
            adherence_rate=adherence_rate,
        )

    def _count_events(
        self,
        events: list[DeviceEvent],
        event_type: DeviceEventType,
    ) -> int:
        return sum(1 for event in events if event.event_type == event_type.value)
