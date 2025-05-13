from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession

from .async_base_repository import AsyncRepository
from ..models.user import UserDB
from ...utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class UsersRepository(AsyncRepository[UserDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, UserDB, "users")

    async def get_by_user_id(self, user_id: int, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[UserDB]:
        try:
            doc = await self.collection().find_one({"tg_id": user_id}, session=session)
            if not doc:
                return SimpleErrorResult(message=f"Document for user {user_id} not found")
            return SimpleOkResult(payload=UserDB(**doc))
        except Exception as e:
            return SimpleErrorResult(message=f"Error retrieving user {user_id}: {str(e)}")

    async def get_open_lecture_participants(self, open_lecture_id: str, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[List[UserDB]]:
        query = {
            "registered_lectures": {
                "$exists": True,
                "$elemMatch": {"$eq": open_lecture_id}
            }
        }
        cursor = self.collection().find(query, session=session)
        try:
            participant = [UserDB(**doc) async for doc in cursor]
            return SimpleOkResult(payload=participant)
        except Exception as e:
            return SimpleErrorResult(message="Participants parsing error: " + str(e))

    async def get_course_participants(self, course_id: str, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[List[UserDB]]:
        query = {
            "registered_courses": {
                "$exists": True,
                "$elemMatch": {"$eq": course_id}
            }
        }
        cursor = self.collection().find(query, session=session)
        try:
            participant = [UserDB(**doc) async for doc in cursor]
            return SimpleOkResult(payload=participant)
        except Exception as e:
            return SimpleErrorResult(message="Participants parsing error: " + str(e))

    async def get_school_participants(self, school_id: str, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[List[UserDB]]:
        query = {
            "registered_schools": {
                "$exists": True,
                "$elemMatch": {"$eq": school_id}
            }
        }
        cursor = self.collection().find(query, session=session)
        try:
            participant = [UserDB(**doc) async for doc in cursor]
            return SimpleOkResult(payload=participant)
        except Exception as e:
            return SimpleErrorResult(message="Participants parsing error: " + str(e))