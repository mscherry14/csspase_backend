from motor.motor_asyncio import AsyncIOMotorDatabase

from .async_base_repository import AsyncRepository
from ..models.user import UserDB
from ...utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class UsersRepository(AsyncRepository[UserDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, UserDB, "users")

    async def get_by_user_id(self, user_id: int) -> SimpleResult[UserDB]:
        try:
            doc = await self.collection().find_one({"tg_id": user_id})
            if not doc:
                return SimpleErrorResult(message=f"Document for user {user_id} not found")
            return SimpleOkResult(payload=UserDB(**doc))
        except Exception as e:
            return SimpleErrorResult(message=f"Error retrieving user {user_id}: {str(e)}")
