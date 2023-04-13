from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.schemas import Token
from src.database import db
from src.user.utils import verify_password
from src.auth.services import create_access_token
from datetime import datetime
from src.auth.exceptions import UsernameNotFoundException, InvalidCredentialsException


router = APIRouter(
    prefix="/login",
    tags=["Authentication"]
)


@router.post("", response_model=Token, status_code=status.HTTP_200_OK)
async def login(login_info: OAuth2PasswordRequestForm = Depends()):
    user = await db["users"].find_one({"username": login_info.username})
    if not user:
        raise UsernameNotFoundException(username=login_info.username)
    elif user and verify_password(login_info.password, user["password"]):
        token = create_access_token(payload={
            "id": user["_id"],
        })
        await db["users"].update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise InvalidCredentialsException()
