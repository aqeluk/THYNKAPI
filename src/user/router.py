import shutil

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.encoders import jsonable_encoder
from src.auth.services import create_access_token
from src.user.services import get_current_user
from src.database import db
from src.user.schemas import User, UserResponse, UserCreate, PasswordReset, PasswordResetRequest
from src.user.utils import get_password_hash
from src.email_handler import send_registration_mail, send_verification_mail, password_reset
import secrets
from PIL import Image
from datetime import datetime
import os
from src.exceptions import ServerErrorException, UserNotFoundException, UnauthorizedUserException, InvalidIdException
from src.user.exceptions import DetailNotAllowedException, VerificationKeyNotFoundException, UserVerifiedException,\
    UserUpdateException


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/registration", response_description="User Sign Up", response_model=UserResponse,
             status_code=status.HTTP_201_CREATED)
async def registration(user_info: UserCreate):
    try:
        user_info = jsonable_encoder(user_info)
        username = await db["users"].find_one({"username": user_info["username"]})
        email = await db["users"].find_one({"email": user_info["email"]})
        if username:
            raise DetailNotAllowedException()
        if email:
            raise DetailNotAllowedException()
        user_info["password"] = get_password_hash(user_info["password"])
        user_info["apiKey"] = secrets.token_hex(20)
        user_info["last_login"] = datetime.utcnow()
        user_info["creation_date"] = datetime.utcnow()
        new_user = await db["users"].insert_one(user_info)
        created_user = await db["users"].find_one({"_id": new_user.inserted_id})
        token = create_access_token({"id": created_user["_id"]})
        verify_link = f"http://localhost:8000/users/verification/?token={token}"
        await send_verification_mail("THYNK Verification", user_info["email"],
                                     {
                                         "title": "E-mail Verification",
                                         "name": user_info["name"],
                                         "verify_link": verify_link
                                     }
                                     )
        return created_user
    except Exception as e:
        raise ServerErrorException(str(e))


@router.get("/verification/", response_description="Verify E-mail")
async def verification(token: str):
    try:
        user = await get_current_user(token)
        if not user:
            raise VerificationKeyNotFoundException()
        elif user["is_verified"]:
            raise UserVerifiedException()
        else:
            await db["users"].update_one(
                {"_id": user["_id"]},
                {"$set": {"is_verified": True}}
            )
            await send_registration_mail("Registration successful", user["email"],
                                         {
                                             "title": "Registration successful",
                                             "name": user["name"]
                                         }
                                         )
            return {"user": user["email"], "message": "User verification successful"}
    except Exception as e:
        raise ServerErrorException(str(e))


@router.get("/verification", response_description="Verify E-mail")
async def resend_verification(user_id: str):
    if user_id == 0:
        raise HTTPException(status_code=400, detail="Invalid user id")
    try:
        user = await db["users"].find_one({"_id": user_id})
        if not user:
            raise VerificationKeyNotFoundException()
        elif user["is_verified"]:
            raise UserVerifiedException()
        else:
            token = create_access_token({"id": user["_id"]})
            verify_link = f"http://localhost:8000/users/verification/?token={token}"
            await send_verification_mail("THYNK Verification", user["email"],
                                         {
                                             "title": "E-mail Verification",
                                             "name": user["name"],
                                             "verify_link": verify_link
                                         }
                                         )
            return {"user": user["email"], "message": "User verification resent successfully"}
    except Exception as e:
        raise ServerErrorException(str(e))


@router.post("/details", response_description="Get user details", response_model=UserResponse)
async def details(current_user=Depends(get_current_user)):
    try:
        user = await db["users"].find_one({"_id": current_user["_id"]})
        return user
    except Exception as e:
        raise ServerErrorException(str(e))


@router.put("/update", response_description="Update user details", response_model=UserResponse)
async def update_details(user_update: User, current_user=Depends(get_current_user)):
    try:
        user_id = current_user["_id"]
        user_info = jsonable_encoder(user_update)
        user = await db["users"].find_one({"_id": user_id})
        if user is None:
            raise UserNotFoundException("User not found")
        updated_user = await db["users"].update_one(
            {"_id": user_id},
            {"$set": user_info}
        )
        if updated_user.modified_count == 1:
            updated_user = await db["users"].find_one({"_id": user_id})
            updated_user["last_login"] = datetime.utcnow()
            return updated_user
        else:
            raise UserUpdateException("Could not update user details")
    except Exception as e:
        raise ServerErrorException(str(e))


@router.delete("/delete/{user_id}", response_description="Delete a User")
async def delete_user(user_id: str, current_user=Depends(get_current_user)):
    if user_id == 0:
        raise InvalidIdException("Invalid user id")
    try:
        user = await db["users"].find_one({"_id": user_id})
        if user is None:
            raise UnauthorizedUserException("User not found")
        # Delete user's associated todos
        await db["todos"].delete_many({"author_id": user_id})
        # Delete user's associated blogs
        await db["blogs"].delete_many({"author_id": user_id})
        # Delete user
        await db["users"].delete_one({"_id": user_id})
        static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                     'static')
        folder_path = os.path.join(static_folder, f"users/{user_id}")
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise ServerErrorException(str(e))


@router.post("/images/profile")
async def upload_profile_picture(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    try:
        user_id = current_user["_id"]
        filepath = f"./../static/users/{user_id}/"
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        filename = file.filename
        extension = filename.split(".")[1]
        if extension not in ["jpg", "png", "jpeg"]:
            return {"status": "error", "detail": "file extension not allowed"}
        token_name = secrets.token_hex(10) + "." + extension
        generated_name = filepath + token_name
        file_content = await file.read()
        with open(generated_name, "wb") as file:
            file.write(file_content)
        img = Image.open(generated_name)
        img = img.resize(size=(200, 200))
        img.save(generated_name)
        file.close()
        user = await db["users"].find_one({"_id": current_user["_id"]})
        if user:
            user["profile_picture"] = token_name
        else:
            raise UnauthorizedUserException()
        file_url = "localhost:8000" + generated_name[1:]
        return {"status": "ok", "filename": file_url}
    except Exception as e:
        raise ServerErrorException(str(e))


@router.post("/request/", response_description="Password Reset request")
async def reset_request(user_email: PasswordResetRequest):
    user = await db["users"].find_one({"email": user_email.email})
    if user is not None:
        token = create_access_token({"id": user["_id"]})
        reset_link = f"http://localhost:8000/password/reset?token={token}"
        await password_reset("Password Reset", user["email"],
                             {
                                 "title": "Password Reset",
                                 "name": user["name"],
                                 "reset_link": reset_link
                             }
                             )
        return {"msg": "Email has been sent with instructions to reset your password."}
    else:
        raise UserNotFoundException("Your details not found, invalid email address")


@router.put("/reset/", response_description="Reset Password")
async def reset_password(token: str, new_password: PasswordReset):
    try:
        reset_data = {k: v for k, v in new_password.dict().items() if v is not None}
        reset_data["password"] = get_password_hash(reset_data["password"])
        if len(reset_data) >= 1:
            user = await get_current_user(token)
            updating_user = await db["users"].update_one({"_id": user["_id"]}, {"$set": reset_data})
            if updating_user.modified_count == 1:
                updated_user = await db["users"].find_one({"_id": user["_id"]})
                if updated_user is not None:
                    return updated_user
        existing_user = await db["users"].find_one({"_id": user["_id"]})
        if existing_user is not None:
            return existing_user
        raise UserNotFoundException("User not found")
    except Exception as e:
        raise ServerErrorException(str(e))
