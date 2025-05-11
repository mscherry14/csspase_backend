from pydantic_mongo import AsyncAbstractRepository

from ...models.shop.product import ProductDB


class OrdersRepository(AsyncAbstractRepository[ProductDB]):
    class Meta:
        collection_name = "orders"