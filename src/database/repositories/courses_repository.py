from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession
from pydantic import EmailStr

from .async_base_repository import AsyncRepository
from ..models.course import CourseDB
from ...utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class CoursesRepository(AsyncRepository[CourseDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, CourseDB, "courses")

    async def find_all_with_speaker(self, speaker: EmailStr, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[List[CourseDB]]:
        query = {
            "speakers": {
                "$exists": True,
                "$elemMatch": {"$eq": speaker}
            }
        }
        cursor = self.collection().find(query, session=session)
        try:
            lects = [CourseDB(**doc) async for doc in cursor]
            return SimpleOkResult(payload=lects)
        except Exception as e:
            return SimpleErrorResult(message="Courses parsing error: " + str(e))

    async def find_by_event_id(self, event_id: str, session: AsyncIOMotorClientSession | None = None) -> \
    SimpleResult[CourseDB]:
        doc = await self.collection().find_one({"courseId": event_id}, session=session)
        if doc is None:
            return SimpleErrorResult(message="no object found")
        try:
            return SimpleOkResult(payload=CourseDB(**doc))
        except Exception as e:
            return SimpleErrorResult(message="Lectures parsing error: " + str(e))