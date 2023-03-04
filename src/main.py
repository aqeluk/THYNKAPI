from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from csvhandler import router as csvhandler
from starlette.responses import RedirectResponse
from driver import router as driver
from auth import router as auth
from business import router as business
from todos import router as todos
from user import router as user
from wholesale import router as wholesale
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
from config import settings


app = FastAPI(title="THYNK API")
origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="../static"), name="static")


@app.get("/")
def docs():
    return RedirectResponse(url='/docs')


app.include_router(driver.router)
app.include_router(csvhandler.router)
app.include_router(auth.router)
app.include_router(business.router)
app.include_router(todos.router)
app.include_router(user.router)
app.include_router(wholesale.router)


register_tortoise(
    app,
    db_url=settings.postgresql_url,
    modules={'models': ['models', 'business.schemas', 'wholesale.schemas']},
    generate_schemas=True,
    add_exception_handlers=True
)
