from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.schemas import Token
from tortoise.contrib.fastapi import HTTPNotFoundError
from src.user.schemas import User
from src.user.utils import verify_password
from src.auth.services import create_access_token, oauth2_providers, get_oauth2_user
from datetime import datetime
from src.auth.exceptions import UsernameNotFoundException, InvalidCredentialsException
from src.config import settings
from src.user.exceptions import DetailNotAllowedException


router = APIRouter(
    prefix="/login",
    tags=["Authentication"]
)

@router.post("", response_model=Token, status_code=status.HTTP_200_OK)
async def login(login_info: OAuth2PasswordRequestForm = Depends()):
    user = await User.get_or_none(username=login_info.username)
    if not user:
        raise UsernameNotFoundException(username=login_info.username)
    elif user and verify_password(login_info.password, user.password):
        token = create_access_token(payload={
            "id": user.id,
        })
        user.last_login = datetime.utcnow()
        await user.save()
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise InvalidCredentialsException()
    

@router.get("/github/authorize")
async def github_authorize(request: Request):
    auth_url = "https://github.com/login/oauth/authorize"
    query_params = {
        "client_id": settings.github.client_id,
        "redirect_uri": settings.github.redirect_uri,
        "scope": settings.github.scope,
    }

    url = f"{auth_url}?{urlencode(query_params)}"
    return RedirectResponse(url=url)


@router.get("/microsoft/authorize")
async def microsoft_authorize(request: Request):
    auth_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    query_params = {
        "client_id": settings.microsoft_client_id,
        "redirect_uri": settings.microsoft_redirect_uri,
        "scope": settings.microsoft_scope,
        "response_type": "code",
    }

    url = f"{auth_url}?{urlencode(query_params)}"
    return RedirectResponse(url=url)

@router.get("/google/authorize")
async def google_authorize(request: Request):
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    query_params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "scope": settings.google_scope,
        "response_type": "code",
    }

    url = f"{auth_url}?{urlencode(query_params)}"
    return RedirectResponse(url=url)

    
@router.get("/{provider}/redirect", response_model=Token)
async def oauth2_redirect(provider: str, request: Request, code: str):
    oauth2 = oauth2_providers.get(provider)
    if not oauth2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown provider: {provider}")
    access_token = await oauth2.get_access_token(code)
    oauth2_user = await get_oauth2_user(access_token, settings, provider)

    user = await User.get_or_none(email=oauth2_user.email)
    if not user:
        # Register the new user
        user_data = {
            "email": oauth2_user.email,
            "name": oauth2_user.name,
            "is_active": True,
            "is_verified": True,
            "last_login": datetime.utcnow(),
        }
        user = await User.create(**user_data)
    else:
        raise DetailNotAllowedException()
        

    token = create_access_token(payload={"id": user.id})
    return {"access_token": token, "token_type": "bearer"}
