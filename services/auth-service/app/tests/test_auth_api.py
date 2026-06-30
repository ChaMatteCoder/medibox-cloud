import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
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


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"service": "auth-service", "status": "ok"}


def test_register_login_and_me(client: TestClient) -> None:
    register_response = client.post(
        "/auth/register",
        json={
            "name": "Ana Cuidadora",
            "email": "ana@example.com",
            "password": "123456",
            "role": "CAREGIVER",
        },
    )

    assert register_response.status_code == 201
    assert register_response.json()["email"] == "ana@example.com"

    login_response = client.post(
        "/auth/login",
        json={"email": "ana@example.com", "password": "123456"},
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    me_response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert me_response.status_code == 200
    assert me_response.json()["role"] == "CAREGIVER"
