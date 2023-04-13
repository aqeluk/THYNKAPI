from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.csvhandler import router as csvhandler
from starlette.responses import RedirectResponse
from src.driver import router as driver
from src.auth import router as auth
from src.business import router as business
from src.todos import router as todos
from src.user import router as user
from src.wholesale import router as wholesale
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
from src.config import settings
import os
import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()



app = FastAPI(title="THYNK API")
origins = [
    "http://localhost:3000", 
"http://192.168.1.98:3000", 
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.mount("/static", StaticFiles(directory="static"), name="static")


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
    modules={'models': ['src.models', 'src.business.schemas', 'src.wholesale.schemas']},
    generate_schemas=True,
    add_exception_handlers=True
)
