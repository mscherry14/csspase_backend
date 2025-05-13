from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession
from pydantic import EmailStr

from .async_base_repository import AsyncRepository, ModelType
from ..models.person import PersonDB
from ...utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class PeopleRepository(AsyncRepository[PersonDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, PersonDB, "people")

    # async def get_by_email(self, mail: EmailStr, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[PersonDB]:
    #     doc = await self.collection().find_one({"email": mail}, session=session)
    #     if doc is None:
    #         return SimpleErrorResult("No such email")
    #     return SimpleOkResult(PersonDB(**doc))

    async def get_by_user_id(self, user_id: int, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[PersonDB]:
        doc = await self.collection().find_one({"tg_id": user_id}, session=session)
        if doc is None:
            return SimpleErrorResult("No person with such email")
        return SimpleOkResult(PersonDB(**doc))