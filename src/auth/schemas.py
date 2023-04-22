from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: Optional[str] = None
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None

class OAuth2User(BaseModel):
    email: str
    name: str