import motor.motor_asyncio
from src.config import settings


client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
db = client.users_blogs_and_todos
