"""Обучение модели: python -m app.train

Читает data/tickets.csv, обучает модель и сохраняет её в файл MODEL_PATH
(по умолчанию model/model.joblib). Печатает версию и точность.
"""

import os
from pathlib import Path

from app.model import save, train

MODEL_PATH = Path(os.getenv("MODEL_PATH", "model/model.joblib"))


def main() -> None:
    model = train()
    save(model, MODEL_PATH)
    print(f"Модель {model.version}: точность {model.accuracy:.3f}, файл {MODEL_PATH}")


if __name__ == "__main__":
    main()
