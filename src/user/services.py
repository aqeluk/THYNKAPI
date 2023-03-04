from fastapi import Depends, HTTPException
from database import db
from auth.services import verify_access_token, oauth2_scheme


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        current_user_id = verify_access_token(token).id
        current_user = await db["users"].find_one({"_id": current_user_id})
        return current_user
    except HTTPException as e:
        raise e
