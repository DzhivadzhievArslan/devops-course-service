def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_version_default(client):
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": "dev"}
