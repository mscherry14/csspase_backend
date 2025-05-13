from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession

from .async_base_repository import AsyncRepository
from ..models.team import TeamDB
from ...utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class TeamsRepository(AsyncRepository[TeamDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, TeamDB, "teams")

    async def get_competition_teams(self, competition_id: str, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[List[TeamDB]]:
        query = {
            "competition_id": competition_id
        }
        cursor = self.collection().find(query, session=session)
        try:
            participant = [TeamDB(**doc) async for doc in cursor]
            return SimpleOkResult(payload=participant)
        except Exception as e:
            return SimpleErrorResult(message="Competition teams parsing error: " + str(e))