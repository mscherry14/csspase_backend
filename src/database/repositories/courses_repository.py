from motor.motor_asyncio import AsyncIOMotorDatabase

from .async_base_repository import AsyncRepository
from ..models.course import CourseDB
from ...utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class CoursesRepository(AsyncRepository[CourseDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, CourseDB, "courses")