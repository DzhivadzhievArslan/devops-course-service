"""Учебный сервис курса DevOps: список задач."""

import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.db import Base, Task, engine, get_session

# Версия задаётся при сборке образа или выкатке.
# По ней видно, какой образ сейчас работает: это нужно для выкатки и отката.
APP_VERSION = os.getenv("APP_VERSION", "dev")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём таблицы при старте. В учебном сервисе миграций нет.
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Учебный сервис: список задач", lifespan=lifespan)


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None


class TaskOut(BaseModel):
    id: int
    title: str
    done: bool

    model_config = {"from_attributes": True}


@app.get("/health")
def health():
    """Процесс жив. База не проверяется."""
    return {"status": "ok"}


@app.get("/ready")
def ready(response: Response, session: Session = Depends(get_session)):
    """Сервис готов принимать запросы: база отвечает."""
    try:
        session.execute(text("SELECT 1"))
    except Exception:
        response.status_code = 503
        return {"status": "database unavailable"}
    return {"status": "ready"}


@app.get("/version")
def version():
    return {"version": APP_VERSION}


@app.get("/tasks", response_model=list[TaskOut])
def list_tasks(session: Session = Depends(get_session)):
    return session.scalars(select(Task).order_by(Task.id)).all()


@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(data: TaskIn, session: Session = Depends(get_session)):
    task = Task(title=data.title, done=False)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def get_task_or_404(task_id: int, session: Session) -> Task:
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, session: Session = Depends(get_session)):
    return get_task_or_404(task_id, session)


@app.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, data: TaskUpdate, session: Session = Depends(get_session)):
    task = get_task_or_404(task_id, session)
    if data.title is not None:
        task.title = data.title
    if data.done is not None:
        task.done = data.done
    session.commit()
    session.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = get_task_or_404(task_id, session)
    session.delete(task)
    session.commit()
