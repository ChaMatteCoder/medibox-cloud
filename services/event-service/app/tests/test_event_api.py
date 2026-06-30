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
os.environ["RABBITMQ_URL"] = "amqp://guest:guest@localhost:5672/"

from app.db.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.messaging.rabbitmq import RabbitMQPublisher  # noqa: E402


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
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

    def fake_publish_notification(self: RabbitMQPublisher, message: dict) -> None:
        published_messages.append(message)

    published_messages: list[dict] = []
    monkeypatch.setattr(
        RabbitMQPublisher,
        "publish_notification",
        fake_publish_notification,
    )
    app.state.published_messages = published_messages
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
    assert response.json() == {"service": "event-service", "status": "ok"}


def test_create_and_list_events(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    create_response = client.post(
        "/events",
        headers=auth_headers,
        json={
            "patient_id": "patient-1",
            "medication_id": "medication-1",
            "event_type": "DOSE_MISSED",
            "payload": {"source": "test"},
        },
    )

    assert create_response.status_code == 201
    event = create_response.json()
    assert event["event_type"] == "DOSE_MISSED"

    list_response = client.get("/events", headers=auth_headers)

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert app.state.published_messages[0]["event_id"] == event["id"]
