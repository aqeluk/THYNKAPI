import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from tortoise.contrib.test import initializer, finalizer
from src.user.schemas import User_Pydantic, UserCreate
from src.user.router import router as user_router

app = FastAPI()
app.include_router(user_router)


@pytest.fixture(scope="module", autouse=True)
def init_db():
    initializer(["src.user.schemas"])
    yield
    finalizer()


@pytest.fixture
def client():
    client = TestClient(app)
    return client


@pytest.fixture
async def test_user():
    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpassword",
        name="Test User",
    )
    user = await User_Pydantic.from_orm(user_create)
    return user


async def test_registration(client: TestClient):
    user_create = UserCreate(
        username="testuser",
        email="test@example.com",
        password="testpassword",
        name="Test User",
    )
    response = client.post("/users/registration", json=user_create.dict())
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_create.username
    assert data["email"] == user_create.email


async def test_get_current_user(client: TestClient, test_user: User_Pydantic):
    response = client.get("/users/details")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


async def test_update_user(client: TestClient, test_user: User_Pydantic):
    user_update = {"name": "Updated Test User"}
    response = client.put("/users/update", json=user_update)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == user_update["name"]


async def test_delete_user(client: TestClient, test_user: User_Pydantic):
    response = client.delete(f"/users/delete/{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User deleted successfully"


async def test_upload_profile_picture(client: TestClient, test_user: User_Pydantic):
    with open("test_image.png", "rb") as f:
        response = client.post(
            "/users/images/profile", files={"file": ("test_image.png", f, "image/png")}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


async def test_password_reset_request(client: TestClient, test_user: User_Pydantic):
    response = client.post(
        "/users/request/", json={"email": test_user.email}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["msg"] == "Email has been sent with instructions to reset your password."
