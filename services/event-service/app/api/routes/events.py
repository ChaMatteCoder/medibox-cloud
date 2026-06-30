from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import DeviceEvent
from app.schemas.event import DeviceEventCreate, DeviceEventRead
from app.services.event_service import EventService

router = APIRouter()


@router.post("", response_model=DeviceEventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: DeviceEventCreate,
    _: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeviceEvent:
    return EventService(db).create(payload)


@router.get("", response_model=list[DeviceEventRead])
def list_events(
    _: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DeviceEvent]:
    return EventService(db).list_all()


@router.get("/patient/{patient_id}", response_model=list[DeviceEventRead])
def list_events_by_patient(
    patient_id: str,
    _: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DeviceEvent]:
    return EventService(db).list_by_patient(patient_id)
