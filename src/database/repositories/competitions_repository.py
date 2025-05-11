from motor.motor_asyncio import AsyncIOMotorDatabase

from .async_base_repository import AsyncRepository
from ..models.competition import CompetitionDB
from ...utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class CompetitionsRepository(AsyncRepository[CompetitionDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, CompetitionDB, "competitions")