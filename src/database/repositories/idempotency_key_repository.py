from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession
from datetime import datetime

from src.utils.simple_result import SimpleResult, SimpleErrorResult, SimpleOkResult
from .async_base_repository import AsyncRepository
from ..models.idempotency_key import IdempotencyKeyDB


class IdempotencyKeyRepository(AsyncRepository[IdempotencyKeyDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, IdempotencyKeyDB, "idempotencyKeys")

    async def setup_index(self):
        try:
            await self.collection().create_index(
                [("expires_at", 1)],
                expireAfterSeconds=0,
                name="ttl_expires_at"
            )
        except Exception as e:
            print("TTL index creation error:", e)

    async def find_one_by_key(self, key: str, session: AsyncIOMotorClientSession | None = None) -> IdempotencyKeyDB | None:
        """Can throw exception"""
        doc = await self.collection().find_one({"key": key}, session=session)
        if not doc:
            return None
        return self._model(**doc)

    async def delete_all(self, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[bool]:
        try:
            result = await self.collection().delete_many(filter={}, session=session)
            if result.deleted_count:
                return SimpleOkResult(payload=True)
            return SimpleErrorResult(f"No documents found")
        except Exception as e:
            return SimpleErrorResult(str(e))