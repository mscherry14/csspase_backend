from pydantic_mongo import AsyncAbstractRepository

from ...models.shop.product import ProductDB


class ProductsRepository(AsyncAbstractRepository[ProductDB]):
    class Meta:
        collection_name = "products"