from fastapi import Depends, HTTPException
from tortoise.exceptions import DoesNotExist
from src.user.schemas import User
from src.auth.services import verify_access_token, oauth2_scheme


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        current_user_id = verify_access_token(token).id
        try:
            current_user = await User.get(id=current_user_id)
            return current_user
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException as e:
        raise e