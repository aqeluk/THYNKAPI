from datetime import datetime
from typing import Optional
from src.models import PyObjectId
from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr, validator, constr


class User(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    username: constr(regex="^[A-Za-z0-9-_]+$", to_lower=True, strip_whitespace=True)
    email: EmailStr = Field(...)
    is_verified: Optional[bool] = Field(default=False)
    profile_picture: Optional[str] = Field(None, max_length=255)
    last_login: Optional[datetime] = Field(default=datetime.utcnow())
    creation_date: Optional[datetime] = Field(default=datetime.utcnow())

    @validator('profile_picture', pre=True, always=True)
    def profile_picture_default(cls, value):
        return value or "https://example.com/default_profile_picture.jpg"

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "John Doe",
                "username": "jdoe91",
                "email": "jdoe@example.com",
                "profile_picture": "https://example.com/profile.jpg"
            }
        }


class UserCreate(User):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    password: Optional[str] = Field(..., min_length=8)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "John Doe",
                "username": "jdoe91",
                "email": "jdoe@example.com",
                "password": "secret_code",
                "profile_picture": "https://example.com/profile.jpg"
            }
        }


class UserResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., min_length=2, max_length=50)
    username: constr(regex="^[A-Za-z0-9-_]+$", to_lower=True, strip_whitespace=True)
    email: EmailStr = Field(...)
    is_verified: Optional[bool] = Field(...)
    profile_picture: Optional[str] = Field(None, max_length=255)
    last_login: Optional[datetime] = Field(...)
    creation_date: Optional[datetime] = Field(...)

    @validator('profile_picture', pre=True, always=True)
    def profile_picture_default(cls, value):
        return value or "https://example.com/default_profile_picture.jpg"

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "John Doe",
                "username": "jdoe91",
                "email": "jdoe@example.com"
            }
        }


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(...)


class PasswordReset(BaseModel):
    password: str = Field(..., min_length=8)
