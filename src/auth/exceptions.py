import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class UsernameNotFoundException(HTTPException):
    def __init__(self, username: str):
        super().__init__(status_code=404, detail=f"User by username {username} not found")
        logger.exception(f"UserNotFoundException: User by username {username} not found")


class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid user credentials")
        logger.exception("InvalidCredentialsException: Invalid user credentials")


class TokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Token has expired", headers={"WWW-Authenticate": "Bearer"})
        logger.exception("TokenExpiredException: Token has expired")


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
        logger.exception("InvalidTokenException: Could not validate credentials")


class AccessTokenCreationException(HTTPException):
    def __init__(self):
        super().__init__(status_code=424, detail="Could not create access token")
        logger.exception(f"AccessTokenCreationException: Could not create access token")
