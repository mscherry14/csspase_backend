from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession
from pydantic import EmailStr

from .async_base_repository import AsyncRepository, ModelType
from ..models.open_lecture import OpenLectureDB
from ...utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class OpenLecturesRepository(AsyncRepository[OpenLectureDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, OpenLectureDB, "openLectures")

    async def find_all_with_speaker(self, speaker: EmailStr, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[List[OpenLectureDB]]:
        query = {
            "speakers": {
                "$exists": True,
                "$elemMatch": {"$eq": speaker}
            }
        }
        cursor = self.collection().find(query, session=session)
        try:
            lects = [OpenLectureDB(**doc) async for doc in cursor]
            return SimpleOkResult(payload=lects)
        except Exception as e:
            return SimpleErrorResult(message="Lectures parsing error: " + str(e))

    async def find_by_event_id(self, event_id: str, session: AsyncIOMotorClientSession | None = None) -> \
    SimpleResult[OpenLectureDB]:
        doc = await self.collection().find_one({"openLectureId": event_id}, session=session)
        if doc is None:
            return SimpleErrorResult(message="no object found")
        try:
            return SimpleOkResult(payload=OpenLectureDB(**doc))
        except Exception as e:
            return SimpleErrorResult(message="Lectures parsing error: " + str(e))