"""Учебный сервис курса DevOps: определяет тему обращения в поддержку."""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app import model as ml
from app.db import Base, Prediction, engine, get_session

# Версия сервиса задаётся при сборке образа или выкатке.
# Вместе с версией модели по ней видно, что сейчас работает: это нужно для выкатки и отката.
APP_VERSION = os.getenv("APP_VERSION", "dev")
MODEL_PATH = Path(os.getenv("MODEL_PATH", "model/model.joblib"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём таблицы при старте. В учебном сервисе миграций нет.
    Base.metadata.create_all(engine)
    # Модель загружается один раз. Если файла нет, сервис работает, но /ready отвечает 503.
    app.state.model = ml.load(MODEL_PATH)
    yield


app = FastAPI(title="Учебный сервис: тема обращения в поддержку", lifespan=lifespan)


class PredictIn(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


class PredictionOut(BaseModel):
    id: int
    text: str
    label: str
    confidence: float
    model_version: str
    created_at: datetime

    model_config = {"from_attributes": True}


def get_model() -> ml.TrainedModel:
    model = app.state.model
    if model is None:
        raise HTTPException(status_code=503, detail="Модель не загружена")
    return model


@app.get("/health")
def health():
    """Процесс жив. База и модель не проверяются."""
    return {"status": "ok"}


@app.get("/ready")
def ready(response: Response, session: Session = Depends(get_session)):
    """Сервис готов принимать запросы: база отвечает и модель загружена."""
    try:
        session.execute(text("SELECT 1"))
    except Exception:
        response.status_code = 503
        return {"status": "database unavailable"}
    if app.state.model is None:
        response.status_code = 503
        return {"status": "model not loaded"}
    return {"status": "ready"}


@app.get("/version")
def version():
    model = app.state.model
    return {
        "version": APP_VERSION,
        "model_version": model.version if model else None,
        "model_accuracy": model.accuracy if model else None,
    }


@app.post("/predict", response_model=PredictionOut, status_code=201)
def predict(
    data: PredictIn,
    session: Session = Depends(get_session),
    model: ml.TrainedModel = Depends(get_model),
):
    label, confidence = model.predict(data.text)
    record = Prediction(
        text=data.text,
        label=label,
        confidence=round(confidence, 3),
        model_version=model.version,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@app.get("/predictions", response_model=list[PredictionOut])
def list_predictions(
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_session),
):
    """Последние предсказания, новые сверху."""
    query = select(Prediction).order_by(Prediction.id.desc()).limit(limit)
    return session.scalars(query).all()
