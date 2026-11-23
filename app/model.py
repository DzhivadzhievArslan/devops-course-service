"""Модель: определяет тему обращения в поддержку по тексту.

Темы: payment (оплата), delivery (доставка), refund (возврат), account (аккаунт).
Модель — TF-IDF по буквенным n-граммам и логистическая регрессия из scikit-learn.
Она обучается за секунды и весит мало, поэтому образ сервиса остаётся небольшим.
"""

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "tickets.csv"

# Параметры обучения. Если их поменять, поменяется и версия модели.
PARAMS = {"ngram_range": (2, 5), "C": 10.0, "test_size": 0.25, "random_state": 42}


@dataclass
class TrainedModel:
    pipeline: Pipeline
    version: str
    accuracy: float

    def predict(self, text: str) -> tuple[str, float]:
        probabilities = self.pipeline.predict_proba([text])[0]
        best = probabilities.argmax()
        return str(self.pipeline.classes_[best]), float(probabilities[best])


def load_dataset(path: Path = DATA_PATH) -> tuple[list[str], list[str]]:
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return [r["text"] for r in rows], [r["label"] for r in rows]


def model_version(path: Path = DATA_PATH) -> str:
    """Версия модели = отпечаток данных и параметров. Те же данные — та же версия."""
    digest = hashlib.sha256(path.read_bytes())
    digest.update(json.dumps(PARAMS, sort_keys=True).encode())
    return digest.hexdigest()[:12]


def train(path: Path = DATA_PATH) -> TrainedModel:
    texts, labels = load_dataset(path)
    # Часть примеров откладываем: на них модель не учится, по ним считаем точность.
    x_train, x_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=PARAMS["test_size"],
        random_state=PARAMS["random_state"],
        stratify=labels,
    )
    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(analyzer="char_wb", ngram_range=PARAMS["ngram_range"]),
            ),
            ("clf", LogisticRegression(C=PARAMS["C"], max_iter=1000)),
        ]
    )
    pipeline.fit(x_train, y_train)
    accuracy = accuracy_score(y_test, pipeline.predict(x_test))
    return TrainedModel(pipeline, model_version(path), round(float(accuracy), 3))


def save(model: TrainedModel, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load(path: Path) -> TrainedModel | None:
    # joblib загружает файл через pickle: открывать можно только свою модель,
    # собранную своим конвейером. Чужой файл модели может выполнить любой код.
    if not path.exists():
        return None
    return joblib.load(path)
