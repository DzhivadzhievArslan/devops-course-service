import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import model as ml
from app.db import Base, get_session
from app.main import app


@pytest.fixture(scope="session")
def trained_model():
    # Обучаем модель один раз на все тесты: это занимает около секунды.
    return ml.train()


@pytest.fixture
def client(trained_model):
    # Каждый тест получает свою пустую базу SQLite в памяти.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    def override_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        # Подменяем модель после старта: файла модели в тестах нет.
        app.state.model = trained_model
        yield test_client
    app.dependency_overrides.clear()
