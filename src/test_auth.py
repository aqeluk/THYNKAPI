import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.user.schemas import UserCreate, User_Pydantic, User

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module", autouse=True)
def init_db():
    from tortoise.contrib.test import initializer, finalizer
    initializer(["src.user.schemas"])
    yield
    finalizer()

@pytest.mark.asyncio
async def create_user(user_create: UserCreate, client: TestClient) -> User_Pydantic:
    user = User(**user_create.dict())
    await user.save()
    return await User_Pydantic.from_tortoise_orm(user)

@pytest.mark.asyncio
async def test_login_success(client):
    user_create = UserCreate(username="testuser", email="test@example.com", password="testpassword", name="Test User")
    user = await create_user(user_create, client)

    response = client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "testpassword",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_unknown_user(client):
    response = client.post(
        "/login",
        data={"username": "unknownuser", "password": "testpassword"},
    )
    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]
