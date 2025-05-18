from motor.motor_asyncio import AsyncIOMotorClient

from src.config import settings

# Подключение к MongoDB через Motor
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.MONGODB_NAME]
