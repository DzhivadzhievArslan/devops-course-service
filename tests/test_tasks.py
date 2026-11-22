def test_empty_list(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_get(client):
    created = client.post("/tasks", json={"title": "Поставить Docker"})
    assert created.status_code == 201
    task = created.json()
    assert task["title"] == "Поставить Docker"
    assert task["done"] is False

    response = client.get(f"/tasks/{task['id']}")
    assert response.status_code == 200
    assert response.json() == task


def test_empty_title_rejected(client):
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422


def test_mark_done(client):
    task = client.post("/tasks", json={"title": "Сделать commit"}).json()
    response = client.patch(f"/tasks/{task['id']}", json={"done": True})
    assert response.status_code == 200
    assert response.json()["done"] is True


def test_delete(client):
    task = client.post("/tasks", json={"title": "Удалить меня"}).json()
    assert client.delete(f"/tasks/{task['id']}").status_code == 204
    assert client.get(f"/tasks/{task['id']}").status_code == 404


def test_missing_task(client):
    assert client.get("/tasks/999").status_code == 404
