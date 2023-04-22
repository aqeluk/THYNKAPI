import os
import shutil

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
import secrets
from PIL import Image
from tortoise.exceptions import DoesNotExist
from src.business.schemas import user_business_pydantic, user_business_pydanticIn, user_product_pydantic,\
    user_product_pydanticIn, UserProduct, UserBusiness
from src.database import db
from datetime import datetime
from src.user.services import get_current_user
from src.exceptions import ServerErrorException, UserNotFoundException, ProductNotFoundException, UnauthorizedUserException,\
    InvalidIdException
from src.business.exceptions import BusinessNotFoundException


router = APIRouter(
    prefix="/business",
    tags=["User Business"]
    )


@router.post('/add')
async def add_user_business(business_info: user_business_pydanticIn,
                            current_user=Depends(get_current_user)):
    try:
        user = await db["users"].find_one({"_id": current_user["_id"]})
        business_details = business_info.dict(exclude_unset=True)
        business_details["creation_date"] = datetime.utcnow()
        business_details["last_updated"] = datetime.utcnow()
        business_details["owner"] = user["_id"]
        business_obj = await UserBusiness.create(**business_details)
        response = await user_business_pydantic.from_tortoise_orm(business_obj)
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        raise UserNotFoundException(str(dne))
    except Exception as e:
        ServerErrorException(str(e))


@router.get('/all')
async def get_user_businesses(current_user=Depends(get_current_user)):
    try:
        response = await user_business_pydantic.from_queryset(UserBusiness.filter(owner=current_user.id))
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        BusinessNotFoundException(str(dne))
    except Exception as e:
        ServerErrorException(str(e))


@router.get('/get/{business_id}')
async def get_specific_user_business(business_id: int):
    if business_id == 0:
        raise InvalidIdException("Invalid business id")
    try:
        response = await user_business_pydantic.from_queryset_single(UserBusiness.get(id=business_id))
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        BusinessNotFoundException(str(dne))
    except Exception as e:
        ServerErrorException(str(e))


@router.put('/update/{business_id}')
async def update_user_business(business_id: int, update_info: user_business_pydanticIn):
    try:
        business = await UserBusiness.get(id=business_id)
        update_info = update_info.dict(exclude_unset=True)
        business.business_name = update_info['business_name']
        business.logo = update_info['logo']
        business.website = update_info['website']
        business.business_description = update_info['business_description']
        business.company_number = update_info['company_number']
        business.vat_number = update_info['vat_number']
        business.last_updated = datetime.utcnow()
        await business.save()
        response = await user_business_pydantic.from_tortoise_orm(business)
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        BusinessNotFoundException(str(dne))
    except Exception as e:
        ServerErrorException(str(e))


@router.delete('/delete/{business_id}')
async def delete_user_business(business_id: int, current_user=Depends(get_current_user)):
    if business_id == 0:
        raise InvalidIdException("Invalid business id")
    business = await UserBusiness.get(id=business_id)
    if current_user["username"] not in ["root", "master"] or current_user.id != business.owner:
        raise HTTPException(status_code=403, detail="User not authorized")
    try:
        try:
            products = await UserProduct.filter(business=business).all()
            if products:
                for product in products:
                    await delete_user_product(product.id)
            try:
                await business.delete()
            except Exception as e:
                ServerErrorException(f"{e}: Internal Server Error while deleting User Business")
        except Exception as e:
            ServerErrorException(f"{e}: Internal Server Error while deleting User Business Products")
        return {"status": "ok", "response": "Successfully deleted User Business and associated products"}
    except DoesNotExist as dne:
        BusinessNotFoundException(str(dne))
    except Exception as e:
        ServerErrorException(str(e))


@router.post('/product/add/{business_id}')
async def add_user_product(business_id: int, product_details: user_product_pydanticIn):
    try:
        business = await UserBusiness.get(id=business_id)
        product_details = product_details.dict(exclude_unset=True)
        business_obj = await UserProduct.create(**product_details, business=business)
        response = await user_product_pydantic.from_tortoise_orm(business_obj)
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        BusinessNotFoundException(str(dne))
    except Exception as e:
        ServerErrorException(str(e))


@router.get('/{business_id}/get/products')
async def get_all_business_products(business_id: int):
    if business_id == 0:
        raise InvalidIdException("Invalid product id")
    try:
        business = await UserBusiness.get(id=business_id)
        response = await user_product_pydantic.from_queryset(UserProduct.filter(business=business))
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        BusinessNotFoundException(str(dne))
    except Exception as e:
        ServerErrorException(str(e))


@router.get('/product/get/{product_id}')
async def get_specific_user_product(product_id: int):
    try:
        response = await user_product_pydantic.from_queryset_single(UserProduct.get(id=product_id))
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        ProductNotFoundException(str(dne))
    except Exception as e:
        ServerErrorException(str(e))


@router.put('/product/update/{product_id}')
async def update_user_product(product_id: int, update_info: user_product_pydanticIn):
    try:
        product = await UserProduct.get(id=product_id)
        update_info = update_info.dict(exclude_unset=True)
        product.name = update_info['name']
        product.category = update_info['category']
        product.price = update_info['price']
        product.description = update_info['description']
        product.last_updated = datetime.utcnow()
        product.cost = update_info['cost']
        await product.save()
        response = await user_product_pydantic.from_tortoise_orm(product)
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        ProductNotFoundException(str(dne))
    except Exception as e:
        ServerErrorException(str(e))


@router.delete('/product/delete/{product_id}')
async def delete_user_product(product_id: int):
    if product_id == 0:
        raise InvalidIdException("Invalid product id")
    try:
        await UserProduct.filter(id=product_id).delete()
        static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                     'static')
        folder_path = os.path.join(static_folder, f"user_products/{product_id}")
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        return {"status": "ok", "message": "product successfully deleted"}
    except DoesNotExist as dne:
        ProductNotFoundException(str(dne))
    except Exception as e:
        ServerErrorException(str(e))


@router.post("/product/upload/{product_id}")
async def create_upload_file(product_id: int, file: UploadFile = File(...),
                             user=Depends(get_current_user)):
    if product_id == 0:
        raise InvalidIdException("Invalid product id")
    try:
        static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                     'static')
        filepath = os.path.join(static_folder, f'user_products/{product_id}/')
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
        product = await UserProduct.get(id=product_id)
        business = await product.business
        if business.owner == user.id:
            product.product_image = token_name
            await product.save()
        else:
            raise UnauthorizedUserException
        file_url = "localhost:8000" + generated_name[1:]
        return {"status": "ok", "filename": file_url}
    except Exception as e:
        ServerErrorException(str(e))
