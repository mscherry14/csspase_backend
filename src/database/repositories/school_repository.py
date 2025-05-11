from motor.motor_asyncio import AsyncIOMotorDatabase

from .async_base_repository import AsyncRepository
from ..models.school import SchoolDB
from ...utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class SchoolsRepository(AsyncRepository[SchoolDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, SchoolDB, "schools")