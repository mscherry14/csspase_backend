from motor.motor_asyncio import AsyncIOMotorDatabase

from .async_base_repository import AsyncRepository
from ..models.open_lecture import OpenLectureDB
from ...utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class OpenLecturesRepository(AsyncRepository[OpenLectureDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, OpenLectureDB, "openLectures")