from fastapi import APIRouter, HTTPException
from src.exceptions import ServerErrorException

from src.driver.services import launch_browser, close_browser, go_to_url, login_to_selleramp, search_ean_on_selleramp,\
    scrape_product_data

router = APIRouter(
    prefix="/selenium",
    tags=["driver"]
    )


@router.on_event("startup")
async def startup_event():
    try:
        await launch_browser()
        return {"message": f"Successfully started"}
    except Exception as e:
        ServerErrorException(str(e))


@router.on_event("shutdown")
async def shutdown_event():
    try:
        await close_browser()
        return {"message": f"Successfully ended"}
    except Exception as e:
        ServerErrorException(str(e))


@router.get("/go_to_url")
async def go_to_url_route(url: str):
    try:
        await go_to_url(url)
        return {"message": f"Successfully navigated to {url}"}
    except Exception as e:
        ServerErrorException(str(e))


@router.get("/login_selleramp")
async def login_selleramp():
    try:
        await login_to_selleramp()
        return {"status": "ok", "message": "Logged in to SellerAMP successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        ServerErrorException(str(e))


@router.get("/selleramp/search/{ean}")
async def search_selleramp(ean: str):
    try:
        await search_ean_on_selleramp(ean)
        return {"status": "ok", "message": f"Loaded up data for EAN {ean} successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        ServerErrorException(str(e))


@router.get("/selleramp/scrape/{cost}")
async def scrape_selleramp(cost: float):
    try:
        data = await scrape_product_data(cost)
        return {"status": "ok", "message": f"Scraped data successfully. + {data}"}
    except HTTPException as e:
        raise e
    except Exception as e:
        ServerErrorException(str(e))

