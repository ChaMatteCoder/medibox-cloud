from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.schemas.event import AdherenceSummary
from app.services.event_service import EventService

router = APIRouter()


@router.get("/{patient_id}/adherence-summary", response_model=AdherenceSummary)
def get_patient_adherence_summary(
    patient_id: str,
    _: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AdherenceSummary:
    return EventService(db).get_adherence_summary(patient_id)
