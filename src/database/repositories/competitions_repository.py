from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession
from pydantic import EmailStr

from .async_base_repository import AsyncRepository
from ..models.competition import CompetitionDB
from ...utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class CompetitionsRepository(AsyncRepository[CompetitionDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, CompetitionDB, "competitions")

    async def find_all_with_speaker(self, speaker: EmailStr, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[List[CompetitionDB]]:
        query = {
            "speakers": {
                "$exists": True,
                "$elemMatch": {"$eq": speaker}
            }
        }
        cursor = self.collection().find(query, session=session)
        try:
            lects = [CompetitionDB(**doc) async for doc in cursor]
            return SimpleOkResult(payload=lects)
        except Exception as e:
            return SimpleErrorResult(message="Lectures parsing error: " + str(e))

    async def find_by_event_id(self, event_id: str, session: AsyncIOMotorClientSession | None = None) -> \
    SimpleResult[CompetitionDB]:
        doc = await self.collection().find_one({"competitionId": event_id}, session=session)
        if doc is None:
            return SimpleErrorResult(message="no object found")
        try:
            return SimpleOkResult(payload=CompetitionDB(**doc))
        except Exception as e:
            return SimpleErrorResult(message="Lectures parsing error: " + str(e))