from app.main import app


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Тема обращения" in response.text


def test_ready(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_not_ready_without_model(client):
    app.state.model = None
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "model not loaded"}


def test_version(client, trained_model):
    response = client.get("/version")
    assert response.status_code == 200
    body = response.json()
    assert body["version"] == "dev"
    assert body["model_version"] == trained_model.version
