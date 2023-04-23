import os
import secrets
import shutil
from PIL import Image
from fastapi import APIRouter, UploadFile, File, Depends
from tortoise.exceptions import DoesNotExist
from src.wholesale.schemas import wholesale_business_pydantic, wholesale_business_pydanticIn, wholesale_product_pydantic,\
    wholesale_product_pydanticIn, wholesale_scraped_product_pydantic, wholesale_scraped_product_pydanticIn,\
    WholesaleProduct, WholesaleBusiness, WholesaleScrapedProduct
from datetime import datetime
from fastapi import HTTPException
from src.user.services import get_current_user
from src.exceptions import ServerErrorException, UnauthorizedUserException, ProductNotFoundException, InvalidIdException
from src.wholesale.exceptions import WholesaleNotFoundException


router = APIRouter(
    prefix="/wholesale",
    tags=["Wholesale"]
    )


@router.post('/add')
async def add_wholesaler(wholesale_info: wholesale_business_pydanticIn, current_user: User_Pydantic = Depends(get_current_user)):
    if current_user.username not in ["root", "master"]:
        raise UnauthorizedUserException()
    try:
        wholesale_info_dict = wholesale_info.dict(exclude_unset=True)
        wholesale_info_dict['creation_date'] = datetime.utcnow()
        wholesale_info_dict['last_updated'] = datetime.utcnow()
        wholesale_obj = await WholesaleBusiness.create(**wholesale_info_dict)
        response = await wholesale_business_pydantic.from_tortoise_orm(wholesale_obj)
        return {"status": "ok", "data": response}
    except Exception as e:
        raise ServerErrorException(str(e))


@router.get('/all')
async def get_all_wholesalers():
    try:
        response = await wholesale_business_pydantic.from_queryset(WholesaleBusiness.all())
        return {"status": "ok", "data": response}
    except Exception as e:
        WholesaleNotFoundException(str(e))


@router.get('/get/{wholesale_id}')
async def get_specific_wholesale(wholesale_id: int):
    if wholesale_id == 0:
        raise HTTPException(status_code=400, detail="Invalid wholesale id")
    try:
        response = await wholesale_business_pydantic.from_queryset_single(WholesaleBusiness.get(id=wholesale_id))
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        raise WholesaleNotFoundException(str(dne))
    except Exception as e:
        raise ServerErrorException(str(e))


@router.put('/update/{wholesale_id}')
async def update_wholesale(wholesale_id: int, update_info: wholesale_business_pydanticIn,
                           current_user=Depends(get_current_user)):
    if current_user["username"] not in ["root", "master"]:
        raise HTTPException(status_code=403, detail="User not authorized")
    if wholesale_id == 0:
        raise HTTPException(status_code=400, detail="Invalid wholesale id")
    try:
        wholesale = await WholesaleBusiness.get(id=wholesale_id)
        update_info = update_info.dict(exclude_unset=True)
        wholesale.business_name = update_info['business_name']
        wholesale.logo = update_info['logo']
        wholesale.website = update_info['website']
        wholesale.correspondence = update_info['correspondence']
        wholesale.email = update_info['email']
        wholesale.phone = update_info['phone']
        wholesale.address = update_info['address']
        wholesale.category = update_info['category']
        wholesale.last_updated = datetime.utcnow()
        await wholesale.save()
        response = await wholesale_business_pydantic.from_tortoise_orm(wholesale)
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        raise WholesaleNotFoundException(str(dne))
    except Exception as e:
        raise ServerErrorException(str(e))


@router.delete('/delete/{wholesale_id}')
async def delete_wholesale(wholesale_id: int, current_user=Depends(get_current_user)):
    if current_user["username"] not in ["root", "master"]:
        raise HTTPException(status_code=403, detail="User not authorized")
    if wholesale_id == 0:
        raise HTTPException(status_code=400, detail="Invalid wholesale id")
    try:
        wholesaler = await WholesaleBusiness.get(id=wholesale_id)
        try:
            wholesale_products = await WholesaleProduct.filter(business=wholesaler).all()
            scraped_wholesale_products = await WholesaleScrapedProduct.filter(business=wholesaler).all()
            if wholesale_products:
                for product in wholesale_products:
                    await delete_wholesale_product(wholesale_id, product.id)
            if scraped_wholesale_products:
                for product in scraped_wholesale_products:
                    await delete_scraped_wholesale_product(wholesale_id, product.id)
            await WholesaleProduct.filter(business=wholesaler).delete()
            await WholesaleScrapedProduct.filter(business=wholesaler).delete()
        except Exception as e:
            print(e)
            return {"status": "error", "detail": "Internal Server Error while deleting Wholesale Products"}
        try:
            await wholesaler.delete()
        except Exception as e:
            print(e)
            return {"status": "error", "detail": "Internal Server Error while deleting Wholesaler"}
        return {"status": "ok", "response": "Successfully deleted Wholesaler and associated products"}
    except DoesNotExist as dne:
        raise WholesaleNotFoundException(str(dne))
    except Exception as e:
        raise ServerErrorException(str(e))


@router.post('/product/add/{wholesale_id}')
async def add_wholesale_product(wholesale_id: int, product_details: wholesale_product_pydanticIn):
    if wholesale_id == 0:
        raise HTTPException(status_code=400, detail="Invalid wholesale id")
    try:
        wholesale = await WholesaleBusiness.get(id=wholesale_id)
        product_details_dict = product_details.dict(exclude_unset=True)
        product_details_dict['creation_date'] = datetime.utcnow()
        product_details_dict['last_updated'] = datetime.utcnow()
        product_obj = await WholesaleProduct.create(**product_details_dict, business=wholesale)
        response = await wholesale_product_pydantic.from_tortoise_orm(product_obj)
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        raise WholesaleNotFoundException(str(dne))
    except Exception as e:
        raise ServerErrorException(str(e))


@router.get('/product/get/{wholesale_id}/products')
async def get_all_wholesaler_products(wholesale_id: int):
    if wholesale_id == 0:
        raise HTTPException(status_code=400, detail="Invalid product id")
    try:
        wholesaler = await WholesaleBusiness.get(id=wholesale_id)
        response = await wholesale_product_pydantic.from_queryset(WholesaleProduct.filter(business=wholesaler))
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        raise WholesaleNotFoundException(str(dne))
    except Exception as e:
        raise ServerErrorException(str(e))


@router.get('/product/get/{product_id}')
async def get_specific_wholesale_product(product_id: int):
    if product_id == 0:
        raise HTTPException(status_code=400, detail="Invalid product id")
    try:
        response = await wholesale_product_pydantic.from_queryset_single(WholesaleProduct.get(id=product_id))
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        raise ProductNotFoundException(str(dne))
    except Exception as e:
        raise ServerErrorException(str(e))


@router.put('/product/update/{product_id}')
async def update_wholesale_product(product_id: int, update_info: wholesale_product_pydanticIn):
    if product_id == 0:
        raise HTTPException(status_code=400, detail="Invalid product id")
    try:
        product = await WholesaleProduct.get(id=product_id)
        update_info = update_info.dict(exclude_unset=True)
        product.name = update_info['name']
        product.category = update_info['category']
        product.price = update_info['price']
        product.description = update_info['description']
        product.last_updated = datetime.utcnow()
        await product.save()
        response = await wholesale_product_pydantic.from_tortoise_orm(product)
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        raise ProductNotFoundException(str(dne))
    except Exception as e:
        raise ServerErrorException(str(e))


@router.delete('/product/delete/{wholesale_id}/{product_id}')
async def delete_wholesale_product(wholesale_id: int, product_id: int):
    if product_id == 0:
        raise HTTPException(status_code=400, detail="Invalid product id")
    try:
        product = await WholesaleProduct.get(id=product_id)
        await product.delete()
        static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                     'static')
        folder_path = os.path.join(static_folder, f"wholesale_products/{wholesale_id}/{product_id}")
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        return {"status": "ok"}
    except DoesNotExist as dne:
        raise ProductNotFoundException(str(dne))
    except Exception as e:
        raise ServerErrorException(str(e))


@router.post("/product/images/{wholesale_id}/{product_id}")
async def create_upload_file(wholesale_id: int, product_id: int, file: UploadFile = File(...)):
    if wholesale_id == 0 or product_id == 0:
        raise HTTPException(status_code=400, detail="Invalid ID combination provided")
    try:
        static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                     'static')
        filepath = os.path.join(static_folder, f"wholesale_products/{wholesale_id}/{product_id}/")
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
        product = await WholesaleProduct.get(id=product_id)
        business = await product.business
        if business:
            product.product_image = token_name
            await product.save()
        else:
            raise UnauthorizedUserException()
        file_url = "localhost:8000" + generated_name[1:]
        return {"status": "ok", "filename": file_url}
    except Exception as e:
        raise ServerErrorException(str(e))


@router.post('/product/scraped/add/{wholesale_id}/{product_id}')
async def add_scraped_wholesale_product(wholesale_id: int, product_id: int,
                                        product_details: wholesale_scraped_product_pydanticIn):
    if wholesale_id == 0 or product_id == 0:
        raise HTTPException(status_code=400, detail="Invalid ID combination provided")
    try:
        product = await WholesaleProduct.get(id=product_id)
        wholesale = await WholesaleBusiness.get(id=wholesale_id)
        product_details_dict = product_details.dict(exclude_unset=True)
        product_details_dict['price'] = product.price
        product_details_dict['creation_date'] = datetime.utcnow()
        product_details_dict['last_updated'] = datetime.utcnow()
        scraped_obj = await WholesaleScrapedProduct.create(**product_details_dict, business=wholesale, product=product)
        response = await wholesale_scraped_product_pydantic.from_tortoise_orm(scraped_obj)
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        raise WholesaleNotFoundException(str(dne))
    except Exception as e:
        raise ServerErrorException(str(e))


@router.get('/product/scraped/get/{wholesale_id}/products')
async def get_all_scraped_wholesaler_products(wholesale_id: int):
    if wholesale_id == 0:
        raise InvalidIdException("Invalid product id")
    try:
        wholesaler = await WholesaleBusiness.get(id=wholesale_id)
        response = await wholesale_scraped_product_pydantic.from_queryset(WholesaleScrapedProduct.filter(business=
                                                                                                         wholesaler))
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        raise WholesaleNotFoundException(str(dne))
    except Exception as e:
        raise ServerErrorException(str(e))


@router.get('/product/scraped/get/{product_id}')
async def get_specific_scraped_wholesale_product(product_id: int):
    if product_id == 0:
        raise HTTPException(status_code=400, detail="Invalid product id")
    try:
        response = await wholesale_scraped_product_pydantic.from_queryset_single(WholesaleScrapedProduct.get(
            id=product_id))
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        raise ProductNotFoundException(str(dne))
    except Exception as e:
        raise ServerErrorException(str(e))


@router.put('/product/scraped/update/{product_id}')
async def update_scraped_wholesale_product(product_id: int, update_info: wholesale_scraped_product_pydanticIn):
    if product_id == 0:
        raise HTTPException(status_code=400, detail="Invalid product id")
    try:
        product = await WholesaleScrapedProduct.get(id=product_id)
        update_info = update_info.dict(exclude_unset=True)
        product.asin = update_info['asin']
        product.ean = update_info['ean']
        product.cost = update_info['cost']
        product.rating = update_info['rating']
        product.reviews = update_info['reviews']
        product.ROI = update_info['ROI']
        product.price = update_info['price']
        product.profit = update_info['profit']
        product.FBA = update_info['FBA']
        product.FBM = update_info['FBM']
        product.AMZ = update_info['AMZ']
        product.last_updated = datetime.utcnow()
        await product.save()
        response = await wholesale_scraped_product_pydantic.from_tortoise_orm(product)
        return {"status": "ok", "data": response}
    except DoesNotExist as dne:
        raise ProductNotFoundException(str(dne))
    except Exception as e:
        raise ServerErrorException(str(e))


@router.delete('/product/scraped/delete/{wholesale_id}/{product_id}')
async def delete_scraped_wholesale_product(wholesale_id: int, product_id: int):
    if product_id == 0:
        raise HTTPException(status_code=400, detail="Invalid product id")
    try:
        await WholesaleScrapedProduct.filter(id=product_id).delete()
        # Delete any files in the associated folder
        static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                     'static')
        folder_path = os.path.join(static_folder, f"wholesale_scraped/{wholesale_id}/{product_id}")
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        return {"status": "ok"}
    except DoesNotExist as dne:
        raise ProductNotFoundException(str(dne))
    except Exception as e:
        raise ServerErrorException(str(e))


@router.post("/product/scraped/{wholesale_id}/{product_id}")
async def create_scraped_upload_file(wholesale_id: int, product_id: int, file: UploadFile = File(...)):
    if wholesale_id == 0 or product_id == 0:
        raise InvalidIdException("Invalid ID combination provided")
    try:
        static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                     'static')
        filepath = os.path.join(static_folder, f"wholesale_scraped/{wholesale_id}/{product_id}/")
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
        product = await WholesaleScrapedProduct.get(id=product_id)
        business = await product.business
        if business:
            product.product_image = token_name
            await product.save()
        else:
            raise UnauthorizedUserException()
        file_url = "localhost:8000" + generated_name[1:]
        return {"status": "ok", "filename": file_url}
    except Exception as e:
        raise ServerErrorException(str(e))
