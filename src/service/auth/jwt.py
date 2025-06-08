import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

from src.config import settings
from src.database.database import db
from src.database.models.auth.refresh_token import RefreshTokenDB
from src.database.repositories.auth.refresh_token_repository import RefreshTokensRepository
from src.utils.simple_result import SimpleErrorResult

# Секретный ключ для подписи JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(e)
        return None


async def create_refresh_token(data: dict):
    to_encode = data.copy()
    user_id = to_encode.get("sub")
    expire = datetime.now(tz=timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    await save_refresh_token(user_id=user_id, refresh_token=encoded_jwt, expire=expire)
    return encoded_jwt


async def save_refresh_token(user_id: int, refresh_token: str, expire: datetime | None = None):
    try:
        token_hash_bytes = bcrypt.hashpw(refresh_token.encode("utf-8"), bcrypt.gensalt())
        token_hash = token_hash_bytes.decode("utf-8")
        # Определяем срок действия
        expires_at = expire or datetime.now(tz=timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        # Создаем запись в базе
        db_token = RefreshTokenDB(
            userId=user_id,
            tokenHash=token_hash,
            expires_at=expires_at,
        )
        res = await RefreshTokensRepository(db=db).insert(db_token)
    except Exception as e:
        pass


async def verify_refresh_token(user_id: int, token: str) -> bool:
    db_tokens = await RefreshTokensRepository(db=db).find_all_by_user(user_id=user_id)

    if not db_tokens or isinstance(db_tokens, SimpleErrorResult):
        return False

    for db_token in db_tokens.payload:
        if bcrypt.checkpw(
                token.encode('utf-8'),  # -> bytes
                db_token.payload.token_hash.encode('utf-8')  # -> bytes
        ):
            await RefreshTokensRepository(db=db).delete(object_id=db_token.id)
            return True
        if db_token.expires_at < datetime.now(tz=timezone.utc):
            await RefreshTokensRepository(db=db).delete(object_id=db_token.id)

    return False
