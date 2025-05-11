from motor.motor_asyncio import AsyncIOMotorDatabase

from .async_base_repository import AsyncRepository
from ..models.person import PersonDB
from ...utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class PeopleRepository(AsyncRepository[PersonDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, PersonDB, "people")