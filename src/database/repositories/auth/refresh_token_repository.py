from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession

from src.utils.simple_result import SimpleResult, SimpleErrorResult, SimpleOkResult
from ..async_base_repository import AsyncRepository
from ...models.auth.refresh_token import RefreshTokenDB


class RefreshTokensRepository(AsyncRepository[RefreshTokenDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, RefreshTokenDB, "refreshTokens")

    async def find_one_by_user(self, user_id: int, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[RefreshTokenDB]:
        try:
            doc = await self.collection().find_one({"userId": user_id}, session=session)
            if not doc:
                return SimpleErrorResult(f"Document with id={user_id} not found")
            return SimpleOkResult(payload=self._model(**doc))
        except Exception as e:
            return SimpleErrorResult(str(e))