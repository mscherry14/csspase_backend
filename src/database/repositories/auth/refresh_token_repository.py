from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession

from src.utils.simple_result import SimpleResult, SimpleErrorResult, SimpleOkResult
from ..async_base_repository import AsyncRepository
from ...models.auth.refresh_token import RefreshTokenDB


class RefreshTokensRepository(AsyncRepository[RefreshTokenDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, RefreshTokenDB, "refreshTokens")

    async def find_one_by_user(self, user_id: int, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[RefreshTokenDB]:
        try:
            doc = await self.collection().find_all({"userId": user_id}, session=session)
            if not doc:
                return SimpleErrorResult(f"Document with id={user_id} not found")
            return SimpleOkResult(payload=self._model(**doc))
        except Exception as e:
            return SimpleErrorResult(str(e))

    async def find_all_by_user(self, user_id: int, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[List[RefreshTokenDB]]:
        res = await self.find_all({"userId": user_id}, session=session)
        return res

    async def delete_all(self, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[bool]:
        try:
            result = await self.collection().delete_many(filter={}, session=session)
            if result.deleted_count:
                return SimpleOkResult(payload=True)
            return SimpleErrorResult(f"No documents found")
        except Exception as e:
            return SimpleErrorResult(str(e))