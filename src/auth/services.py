from typing import Dict
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from .schemas import TokenData
from config import settings
from .exceptions import TokenExpiredException, InvalidTokenException, AccessTokenCreationException


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def create_access_token(payload: Dict):
    try:
        to_encode = payload.copy()
        expiration_time = datetime.utcnow() + timedelta(minutes=60)
        to_encode.update({"exp": expiration_time})
        jw_access_token = jwt.encode(to_encode, key=settings.secret_key, algorithm=settings.algorithm)
        return jw_access_token
    except Exception as e:
        raise AccessTokenCreationException()


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("id")
        if not user_id:
            raise InvalidTokenException()
        token_data = TokenData(id=user_id)
        return token_data
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except (jwt.JWTError, jwt.PyJWTError):
        raise InvalidTokenException()
