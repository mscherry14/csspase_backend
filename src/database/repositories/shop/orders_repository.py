from motor.motor_asyncio import AsyncIOMotorDatabase

from ..async_base_repository import AsyncRepository
from ...models.shop.order import OrderDB
from ....utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class OrdersRepository(AsyncRepository[OrderDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, OrderDB, "orders")