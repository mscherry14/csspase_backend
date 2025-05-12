import os

from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext

from src.database.database import db
from src.database.models.auth.refresh_token import RefreshTokenDB
from src.database.repositories.auth.refresh_token_repository import RefreshTokensRepository

# Секретный ключ для подписи JWT
SECRET_KEY: str = os.getenv("SECRET_KEY", "secret-key-for-dev")  # На практике используйте сложный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        return None

async def create_refresh_token(data: dict):
    to_encode = data.copy()
    user_id = to_encode.get("sub")
    expire = datetime.now(tz=timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    await save_refresh_token(user_id=user_id, refresh_token=encoded_jwt, expire=expire)
    return encoded_jwt

async def save_refresh_token(user_id: int, refresh_token: str, expire: datetime | None = None):
    try:
        #TODO: do hash =(
        token_hash = refresh_token #pwd_context.hash(refresh_token)
        # Определяем срок действия
        expires_at = expire or datetime.now(tz=timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        print(expires_at)
        # Создаем запись в базе
        db_token = RefreshTokenDB(
            userId=user_id,
            tokenHash=token_hash,
            expires_at=expires_at,
        )
        print(db_token.model_dump())
        res = await RefreshTokensRepository(db=db).insert(db_token)
        print(res)
    except Exception as e:
        pass


async def verify_refresh_token(user_id: int, token: str) -> bool:
    # Ищем последний неотозванный токен пользователя
    db_token = await RefreshTokensRepository(db=db).find_one_by_user(user_id=user_id)

    if not db_token:
        return False

    # Проверяем соответствие токена хэшу в базе
    return pwd_context.verify(token, db_token.payload.token_hash)
