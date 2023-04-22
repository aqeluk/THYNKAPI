from typing import Dict
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer
from src.auth.schemas import TokenData, OAuth2User
from src.config import settings as AppSettings
from src.auth.exceptions import TokenExpiredException, InvalidTokenException, AccessTokenCreationException
import httpx


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

class CustomOAuth2AuthorizationCodeBearer(OAuth2AuthorizationCodeBearer):
    def __init__(
        self,
        authorizationUrl: str,
        tokenUrl: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scope: str,
    ):
        super().__init__(authorizationUrl=authorizationUrl, tokenUrl=tokenUrl)
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope

oauth2_providers = {
    "github": CustomOAuth2AuthorizationCodeBearer(
        authorizationUrl=AppSettings.github_server_base_url,
        tokenUrl=AppSettings.github_server_token_url,
        client_id=AppSettings.github_client_id,
        client_secret=AppSettings.github_client_secret,
        redirect_uri=AppSettings.github_redirect_uri,
        scope=AppSettings.github_scope,
    ),
    "microsoft": CustomOAuth2AuthorizationCodeBearer(
        authorizationUrl=AppSettings.microsoft_server_base_url,
        tokenUrl=AppSettings.microsoft_server_token_url,
        client_id=AppSettings.microsoft_client_id,
        client_secret=AppSettings.microsoft_client_secret,
        redirect_uri=AppSettings.microsoft_redirect_uri,
        scope=AppSettings.microsoft_scope,
    ),
    "google": CustomOAuth2AuthorizationCodeBearer(
        authorizationUrl=AppSettings.google_server_base_url,
        tokenUrl=AppSettings.google_server_token_url,
        client_id=AppSettings.google_client_id,
        client_secret=AppSettings.google_client_secret,
        redirect_uri=AppSettings.google_redirect_uri,
        scope=AppSettings.google_scope,
    ),
}


async def get_github_user(access_token: str) -> OAuth2User:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com/user", headers=headers)

    response.raise_for_status()
    user_data = response.json()

    return OAuth2User(email=user_data["email"], name=user_data["name"])

async def get_oauth2_user(access_token: str, settings: AppSettings, provider: str) -> OAuth2User:
    if provider == "github":
        return await get_github_user(access_token)
    elif provider == "microsoft":
        userinfo_url = AppSettings.microsoft.server_userinfo_url
    elif provider == "google":
        userinfo_url = AppSettings.google.server_userinfo_url
    else:
        raise ValueError(f"Unknown provider: {provider}")

    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(userinfo_url, headers=headers)

    response.raise_for_status()
    user_data = response.json()

    if provider == "microsoft":
        user_data = user_data["value"][0]

    return OAuth2User(email=user_data["email"], name=user_data["name"])


def create_access_token(payload: Dict):
    try:
        to_encode = payload.copy()
        expiration_time = datetime.utcnow() + timedelta(minutes=60)
        to_encode.update({"exp": expiration_time})
        jw_access_token = jwt.encode(to_encode, key=AppSettings.secret_key, algorithm=AppSettings.algorithm)
        return jw_access_token
    except Exception as e:
        raise AccessTokenCreationException()


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, AppSettings.secret_key, algorithms=[AppSettings.algorithm])
        user_id: str = payload.get("id")
        if not user_id:
            raise InvalidTokenException()
        token_data = TokenData(id=user_id)
        return token_data
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except (jwt.JWTError, jwt.PyJWTError):
        raise InvalidTokenException()
