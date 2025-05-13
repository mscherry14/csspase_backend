from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession
from pydantic import EmailStr

from .async_base_repository import AsyncRepository
from ..models.school import SchoolDB
from ...utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class SchoolsRepository(AsyncRepository[SchoolDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, SchoolDB, "schools")

    async def find_all_with_speaker(self, speaker: EmailStr, session: AsyncIOMotorClientSession | None = None) -> \
    SimpleResult[List[SchoolDB]]:
        query = {
            "speakers": {
                "$exists": True,
                "$elemMatch": {"$eq": speaker}
            }
        }
        cursor = self.collection().find(query, session=session)
        try:
            lects = [SchoolDB(**doc) async for doc in cursor]
            return SimpleOkResult(payload=lects)
        except Exception as e:
            return SimpleErrorResult(message="Lectures parsing error: " + str(e))

    async def find_by_event_id(self, event_id: str, session: AsyncIOMotorClientSession | None = None) -> \
    SimpleResult[SchoolDB]:
        doc = await self.collection().find_one({"schoolId": event_id}, session=session)
        if doc is None:
            return SimpleErrorResult(message="no object found")
        try:
            return SimpleOkResult(payload=SchoolDB(**doc))
        except Exception as e:
            return SimpleErrorResult(message="Lectures parsing error: " + str(e))