"""Подключение к базе данных и модель задачи."""

import os

from sqlalchemy import Boolean, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

# Адрес базы берётся из переменной окружения.
# Без неё сервис работает с локальным файлом SQLite: так удобно запускать тесты.
# В Docker Compose задаётся PostgreSQL, например:
#   postgresql+psycopg://app:secret@db:5432/app
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    done: Mapped[bool] = mapped_column(Boolean, default=False)


def get_session():
    with Session(engine) as session:
        yield session
