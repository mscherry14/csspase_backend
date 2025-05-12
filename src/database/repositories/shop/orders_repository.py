from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession

from ..async_base_repository import AsyncRepository
from ...models.shop.order import OrderDB
from ....utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class OrdersRepository(AsyncRepository[OrderDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, OrderDB, "orders")

    async def orders_by_user_id(self, user_id: int, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[List[OrderDB]]:
        res = await self.find_all({"recipientId": user_id}, session=session)
        if isinstance(res, SimpleErrorResult):
            return SimpleErrorResult(message=res.message)
        else:
            return SimpleOkResult(payload=res.payload)

    async def order_by_order_id(self, order_id: str, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[OrderDB]:
        try:
            doc = await self.collection().find_one({"orderId": order_id}, session=session)
            if not doc:
                return SimpleErrorResult(f"Order with id={order_id} not found")
            return SimpleOkResult(payload=OrderDB(**doc))
        except Exception as e:
            return SimpleErrorResult(str(e))
