import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["JWT_ALGORITHM"] = "HS256"

from app.db.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    token = jwt.encode(
        {"sub": "caregiver-1", "role": "CAREGIVER"},
        "test-secret",
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"service": "medication-service", "status": "ok"}


def test_create_and_list_patient(client: TestClient, auth_headers: dict[str, str]) -> None:
    create_response = client.post(
        "/patients",
        headers=auth_headers,
        json={"name": "Maria Paciente", "birth_date": "1945-03-10"},
    )

    assert create_response.status_code == 201
    patient = create_response.json()
    assert patient["caregiver_id"] == "caregiver-1"

    list_response = client.get("/patients", headers=auth_headers)

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


def test_create_medication_and_schedule(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    patient_response = client.post(
        "/patients",
        headers=auth_headers,
        json={"name": "Maria Paciente", "birth_date": "1945-03-10"},
    )
    patient_id = patient_response.json()["id"]

    medication_response = client.post(
        "/medications",
        headers=auth_headers,
        json={
            "patient_id": patient_id,
            "name": "Losartana",
            "dosage": "50mg",
            "instructions": "Tomar apos o cafe",
            "active": True,
        },
    )

    assert medication_response.status_code == 201
    medication_id = medication_response.json()["id"]

    schedule_response = client.post(
        "/schedules",
        headers=auth_headers,
        json={
            "medication_id": medication_id,
            "scheduled_time": "08:00:00",
            "weekdays": ["MON", "TUE", "WED", "THU", "FRI"],
        },
    )

    assert schedule_response.status_code == 201
    assert schedule_response.json()["medication_id"] == medication_id

    schedules_response = client.get(
        f"/schedules/patient/{patient_id}",
        headers=auth_headers,
    )

    assert schedules_response.status_code == 200
    assert len(schedules_response.json()) == 1
