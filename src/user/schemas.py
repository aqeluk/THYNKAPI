from datetime import datetime
from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, Field, EmailStr, constr
from typing import Optional


class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, min_length=2)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=255, unique=True, index=True )
    password = fields.CharField(max_length=255)
    is_verified = fields.BooleanField(default=False)
    profile_picture = fields.CharField(max_length=255, null=True)
    last_login = fields.DatetimeField(auto_now_add=True)
    creation_date = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table_description = "user"

    async def validate(self, raise_exception=True):
        if not self.name:
            if raise_exception:
                raise ValueError("Name cannot be empty.")
            else:
                return False
        if not self.username:
            if raise_exception:
                raise ValueError("Username cannot be empty.")
            else:
                return False
        if not self.email:
            if raise_exception:
                raise ValueError("Email cannot be empty.")
            else:
                return False
        return True


User_Pydantic = pydantic_model_creator(User, name="User")
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)
UserUpdate_Pydantic = pydantic_model_creator(User, name="UserUpdate", exclude_readonly=True, exclude=("password", "is_verified", "last_login", "creation_date"))

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    username: constr(regex="^[A-Za-z0-9-_]+$", to_lower=True, strip_whitespace=True)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8)
    profile_picture: str = Field(None, max_length=255)


class UserResponse(BaseModel):
    id: int
    name: str = Field(..., min_length=2, max_length=50)
    username: constr(regex="^[A-Za-z0-9-_]+$", to_lower=True, strip_whitespace=True)
    email: EmailStr = Field(...)
    is_verified: bool = Field(...)
    profile_picture: str = Field(None, max_length=255)
    last_login: datetime = Field(...)
    creation_date: datetime = Field(...)

    class Config:
        orm_mode = True 

class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(...)

class PasswordReset(BaseModel):
    password: str = Field(..., min_length=8)