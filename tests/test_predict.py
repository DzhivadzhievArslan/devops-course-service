import pytest

from app.main import app


@pytest.mark.parametrize(
    ("text", "label"),
    [
        ("С карты дважды списали деньги", "payment"),
        ("Курьер так и не приехал", "delivery"),
        ("Хочу вернуть бракованный товар", "refund"),
        ("Не могу войти в личный кабинет", "account"),
    ],
)
def test_predict_label(client, text, label):
    response = client.post("/predict", json={"text": text})
    assert response.status_code == 201
    body = response.json()
    assert body["label"] == label
    assert 0 < body["confidence"] <= 1


def test_predict_saved(client, trained_model):
    client.post("/predict", json={"text": "Где моя посылка?"})
    response = client.get("/predictions")
    assert response.status_code == 200
    saved = response.json()
    assert len(saved) == 1
    assert saved[0]["text"] == "Где моя посылка?"
    assert saved[0]["model_version"] == trained_model.version


def test_predictions_newest_first(client):
    client.post("/predict", json={"text": "первое"})
    client.post("/predict", json={"text": "второе"})
    texts = [p["text"] for p in client.get("/predictions").json()]
    assert texts == ["второе", "первое"]


def test_empty_text_rejected(client):
    response = client.post("/predict", json={"text": ""})
    assert response.status_code == 422


def test_predict_without_model(client):
    app.state.model = None
    response = client.post("/predict", json={"text": "Где мой заказ?"})
    assert response.status_code == 503
