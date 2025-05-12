from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession

from ..async_base_repository import AsyncRepository
from ...models.shop.product import ProductDB
from ....utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class ProductsRepository(AsyncRepository[ProductDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, ProductDB, "products")

    async def product_by_product_id(self, product_id: str, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[ProductDB]:
        try:
            doc = await self.collection().find_one({"productId": product_id}, session=session)
            if not doc:
                return SimpleErrorResult(f"Order with id={product_id} not found")
            return SimpleOkResult(payload=ProductDB(**doc))
        except Exception as e:
            return SimpleErrorResult(str(e))
