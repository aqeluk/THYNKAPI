import pytest
from fastapi.testclient import TestClient
from main import app  # Replace "main" with the name of your main FastAPI app file
from datetime import datetime

client = TestClient(app)


def login_user(username: str, password: str):
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def access_token():
    return login_user("testuser", "testpassword")  # Replace with valid credentials


def test_create_todo(access_token):
    response = client.post(
        "/todo",
        json={
            "title": "Test Todo",
            "task": "Test task",
            "deadline": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Todo"


def test_get_todos(access_token):
    response = client.get(
        "/todo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_specific_todo(access_token):
    # Replace "test_todo_id" with a valid Todo ID
    test_todo_id = "your_test_todo_id"
    response = client.get(
        f"/todo/{test_todo_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["_id"] == test_todo_id


def test_update_todo(access_token):
    # Replace "test_todo_id" with a valid Todo ID
    test_todo_id = "your_test_todo_id"
    response = client.put(
        f"/todo/{test_todo_id}",
        json={
            "title": "Updated Test Todo",
            "task": "Updated test task",
            "deadline": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Test Todo"


def test_delete_todo(access_token):
    # Replace "test_todo_id" with a valid Todo ID to be deleted
    test_todo_id = "your_test_todo_id"
    response = client.delete(
        f"/todo/{test_todo_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["response"] == "Successfully deleted todo"
