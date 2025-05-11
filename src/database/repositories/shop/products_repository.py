from motor.motor_asyncio import AsyncIOMotorDatabase

from ..async_base_repository import AsyncRepository
from ...models.shop.product import ProductDB
from ....utils.simple_result import SimpleErrorResult, SimpleResult, SimpleOkResult


class ProductsRepository(AsyncRepository[ProductDB]):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, ProductDB, "products")
