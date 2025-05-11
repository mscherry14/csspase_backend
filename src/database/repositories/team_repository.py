from motor.motor_asyncio import AsyncIOMotorDatabase

from .async_base_repository import AsyncRepository
from ..models.team import TeamDB
from ...utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class TeamsRepository(AsyncRepository[TeamDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, TeamDB, "teams")