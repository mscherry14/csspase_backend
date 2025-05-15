from motor.motor_asyncio import AsyncIOMotorClient

from src.config import settings

# Чтение переменных окружения
MONGO_URL = settings.MONGO_URL
MONGO_NAME = settings.MONGO_NAME

# Подключение к MongoDB через Motor
client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_NAME]
