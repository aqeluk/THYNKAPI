from fastapi import status, HTTPException
from fastapi.testclient import TestClient
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import timedelta
from auth.router import router
from auth.services import create_access_token, verify_access_token
from auth.exceptions import (
    UsernameNotFoundException,
    InvalidCredentialsException,
    TokenExpiredException,
    InvalidTokenException,
    AccessTokenCreationException,
)
from main import app
from config import settings
from database import db
from user.utils import create_password_hash


app.include_router(router)
client = TestClient(app)

test_user = {
    "_id": "test-id",
    "username": "test_user",
    "password": create_password_hash("test_password"),
    "email": "test@example.com",
    "last_login": None,
}


async def mock_find_one(*args, **kwargs):
    if kwargs["filter"]["username"] == test_user["username"]:
        return test_user
    return None


async def mock_update_one(*args, **kwargs):
    return None


db["users"].find_one = mock_find_one
db["users"].update_one = mock_update_one


def test_successful_login():
    response = client.post(
        "/login",
        data={
            "username": test_user["username"],
            "password": "test_password",
            "grant_type": "password",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "token_type" in response.json()


def test_username_not_found():
    with pytest.raises(UsernameNotFoundException):
        client.post(
            "/login",
            data={
                "username": "non_existent",
                "password": "test_password",
                "grant_type": "password",
            },
        )


def test_invalid_credentials():
    with pytest.raises(InvalidCredentialsException):
        client.post(
            "/login",
            data={
                "username": test_user["username"],
                "password": "wrong_password",
                "grant_type": "password",
            },
        )


def test_create_access_token():
    payload = {"id": test_user["_id"]}
    token = create_access_token(payload)
    assert isinstance(token, str)


def test_create_access_token_error():
    with pytest.raises(AccessTokenCreationException):
        create_access_token("invalid_payload")


def test_verify_access_token():
    payload = {"id": test_user["_id"]}
    token = create_access_token(payload)
    token_data = verify_access_token(token)
    assert token_data.id == test_user["_id"]


def test_verify_expired_access_token():
    payload = {"id": test_user["_id"], "exp": (datetime.utcnow() - timedelta(minutes=1))}
    token = jwt.encode(payload, key=settings.secret_key, algorithm=settings.algorithm)

    with pytest.raises(TokenExpiredException):
        verify_access_token(token)


def test_verify_invalid_access_token():
    payload = {"id": test_user["_id"]}
    token = jwt.encode(payload, key="wrong_key", algorithm=settings.algorithm)

    with pytest.raises(InvalidTokenException):
        verify_access_token(token)
