from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pymongo import WriteConcern

load_dotenv("../../.env")

# Чтение переменных окружения
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGO_NAME = os.getenv("MONGODB_NAME", "test")

# Подключение к MongoDB через Motor
client = AsyncIOMotorClient(MONGO_URL, write_concern=WriteConcern("majority"))
db = client[MONGO_NAME]
