"""Подключение к базе данных и таблица предсказаний."""

import os
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

# Адрес базы берётся из переменной окружения.
# Без неё сервис работает с локальным файлом SQLite: так удобно запускать тесты.
# В Docker Compose задаётся PostgreSQL, например:
#   postgresql+psycopg://app:secret@db:5432/app
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass


class Prediction(Base):
    """Каждый запрос к модели записывается: что спросили, что ответила, какая версия."""

    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(1000))
    label: Mapped[str] = mapped_column(String(50))
    confidence: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


def get_session():
    with Session(engine) as session:
        yield session
