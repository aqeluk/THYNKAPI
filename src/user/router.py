import shutil

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.encoders import jsonable_encoder
from tortoise.exceptions import DoesNotExist
from src.auth.services import create_access_token
from src.user.services import get_current_user
from src.database import db
from src.todos.schemas import Todo
from src.user.schemas import User, PasswordReset, PasswordResetRequest, UserResponse, UserCreate, UserUpdate_Pydantic, User_Pydantic
from src.user.utils import get_password_hash
from src.email_handler import send_registration_mail, send_verification_mail, password_reset
import secrets
from PIL import Image
from datetime import datetime
import os
import shutil
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
        username_exists = await User.exists(username=user_info["username"])
        email_exists = await User.exists(email=user_info["email"])
        if username_exists or email_exists:
            raise DetailNotAllowedException()

        user_info["password"] = get_password_hash(user_info["password"])
        user_info["apiKey"] = secrets.token_hex(20)
        user_info["last_login"] = datetime.utcnow()
        user_info["creation_date"] = datetime.utcnow()
        user = await User.create(**user_info)

        token = create_access_token({"id": user.id})
        verify_link = f"http://localhost:8000/users/verification/?token={token}"
        await send_verification_mail("THYNK Verification", user_info["email"],
                                     {
                                         "title": "E-mail Verification",
                                         "name": user_info["name"],
                                         "verify_link": verify_link
                                     }
                                     )
        return UserResponse.from_orm(user)
    except Exception as e:
        raise ServerErrorException(str(e))



@router.get("/verification/", response_description="Verify E-mail")
async def verification(token: str):
    try:
        user = await get_current_user(token)
        if not user:
            raise VerificationKeyNotFoundException()
        elif user.is_verified:
            raise UserVerifiedException()
        else:
            await User.filter(id=user.id).update(is_verified=True)
            await send_registration_mail("Registration successful", user.email,
                                         {
                                             "title": "Registration successful",
                                             "name": user.name
                                         }
                                         )
            return {"user": user.email, "message": "User verification successful"}
    except Exception as e:
        raise ServerErrorException(str(e))


@router.get("/verification", response_description="Verify E-mail")
async def resend_verification(user_id: str):
    if user_id == 0:
        raise HTTPException(status_code=400, detail="Invalid user id")
    try:
        user = await User.get_or_none(id=user_id)
        if not user:
            raise VerificationKeyNotFoundException()
        elif user.is_verified:
            raise UserVerifiedException()
        else:
            token = create_access_token({"id": user.id})
            verify_link = f"http://localhost:8000/users/verification/?token={token}"
            await send_verification_mail("THYNK Verification", user.email,
                                         {
                                             "title": "E-mail Verification",
                                             "name": user.name,
                                             "verify_link": verify_link
                                         }
                                         )
            return {"user": user.email, "message": "User verification resent successfully"}
    except Exception as e:
        raise ServerErrorException(str(e))


@router.post("/details", response_description="Get user details", response_model=UserResponse)
async def details(current_user=Depends(get_current_user)):
    try:
        user = await User.get(id=current_user.id)
        return user
    except Exception as e:
        raise ServerErrorException(str(e))

@router.put("/update", response_description="Update user details", response_model=UserResponse)
async def update_user(user_update: UserUpdate_Pydantic, user: User_Pydantic = Depends(get_current_user)):
    try:
        user_obj = await User.get(id=user.id)
        user_obj.name = user_update.name or user_obj.name
        user_obj.username = user_update.username or user_obj.username
        user_obj.email = user_update.email or user_obj.email

        # Save the changes to the database
        await user_obj.save()

        # Convert the updated user object to a UserResponse Pydantic model
        user_response = UserResponse.from_orm(user_obj)

        return user_response
    except Exception as e:
        raise ServerErrorException(str(e))

@router.delete("/delete/{username}", response_description="Delete a User")
async def delete_user(username: str, current_user: User_Pydantic = Depends(get_current_user)):
    if current_user.username not in ['root', 'master']:
        raise UnauthorizedUserException("Only root or master can delete users")
    
    try:
        user = await User.get(username=username)
        if user is None:
            raise UnauthorizedUserException("User not found")
        
        # Delete user's associated todos
        await Todo.filter(author_id=user.id).delete()
        
        # Delete user
        await user.delete()
        static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                     'static')
        folder_path = os.path.join(static_folder, f"users/{user.id}")
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise ServerErrorException(str(e))



@router.post("/images/profile")
async def upload_profile_picture(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    try:
        user_id = await User.get(id=current_user.id)
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
        user = await User.get(id=current_user.id)
        if user:
            user.profile_picture = token_name
            await user.save()
        else:
            raise UnauthorizedUserException()
        file_url = "localhost:8000" + generated_name[1:]
        return {"status": "ok", "filename": file_url}
    except Exception as e:
        raise ServerErrorException(str(e))


@router.post("/request/", response_description="Password Reset request")
async def reset_request(user_email: PasswordResetRequest):
    try:
        user = await User.get(email=user_email.email)
        token = create_access_token({"id": user.id})
        reset_link = f"http://localhost:8000/password/reset?token={token}"
        await password_reset("Password Reset", user.email,
                             {
                                 "title": "Password Reset",
                                 "name": user.name,
                                 "reset_link": reset_link
                             }
                             )
        return {"msg": "Email has been sent with instructions to reset your password."}
    except:
        raise UserNotFoundException("Your details not found, invalid email address")


@router.put("/reset/", response_description="Reset Password")
async def reset_password(token: str, new_password: PasswordReset):
    try:
        reset_data = {k: v for k, v in new_password.dict().items() if v is not None}
        reset_data["password"] = get_password_hash(reset_data["password"])
        if len(reset_data) >= 1:
            user = await get_current_user(token)
            await User.filter(id=user.id).update(password=reset_data["password"])
            updated_user = await User.get(id=user.id)
            if updated_user is not None:
                return updated_user
        existing_user = await User.get(id=user.id)
        if existing_user is not None:
            return existing_user
        raise UserNotFoundException("User not found")
    except Exception as e:
        raise ServerErrorException(str(e))
