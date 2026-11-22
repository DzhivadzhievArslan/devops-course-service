# Учебный сервис: список задач

Небольшой веб-сервис на FastAPI. На нём построен весь курс DevOps:
Git, Docker, Docker Compose, CI/CD.

## Что умеет

| Метод и путь | Что делает |
|---|---|
| `GET /health` | Процесс жив (база не проверяется) |
| `GET /ready` | Сервис готов: база отвечает. Если нет — код 503 |
| `GET /version` | Версия сервиса из переменной `APP_VERSION` |
| `GET /tasks` | Список задач |
| `POST /tasks` | Создать задачу: `{"title": "..."}` |
| `GET /tasks/{id}` | Одна задача |
| `PATCH /tasks/{id}` | Изменить: `{"title": "...", "done": true}` |
| `DELETE /tasks/{id}` | Удалить |

Документация API открывается по адресу http://127.0.0.1:8000/docs.

## Параметры

| Переменная | По умолчанию | Зачем |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./app.db` | Адрес базы. Для PostgreSQL: `postgresql+psycopg://app:secret@db:5432/app` |
| `APP_VERSION` | `dev` | Версия, которую показывает `/version` |

## Запуск на своём компьютере

Нужен Python 3.12 или новее.

```bash
python -m venv .venv
# Windows (Git Bash):  source .venv/Scripts/activate
# macOS и Linux:       source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

## Проверки

```bash
ruff check .            # стиль и типовые ошибки
ruff format --check .   # форматирование
pytest                  # тесты
```

Тесты работают с базой SQLite в памяти, PostgreSQL для них не нужен.
