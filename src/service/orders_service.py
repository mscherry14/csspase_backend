from datetime import datetime, timezone
from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase

from ..database.models import PyObjectId
from ..database.models.banking.utils import TransferStatus
from ..database.models.shop.order import OrderDB, OrderStatus
from ..database.models.shop.product import ProductDB
from ..database.repositories.banking.shop_payments_repository import ShopPaymentsRepository
from ..database.repositories.shop.orders_repository import OrdersRepository
from ..database.repositories.users_repository import UsersRepository
from ..utils.simple_result import SimpleResult, SimpleErrorResult, SimpleOkResult


class OrdersService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_user_orders(self, user_id: int) -> SimpleResult[List[OrderDB]]:
        """
        чекнуть юзера
        из всех заказов достать только заказы юзера
        """
        res = await UsersRepository(db=self.db).get_by_user_id(user_id=user_id)
        if isinstance(res, SimpleErrorResult):
            return SimpleErrorResult('user not found')
        res = await OrdersRepository(self.db).orders_by_user_id(user_id=user_id)
        return res

    async def get_orders(self) -> SimpleResult[List[OrderDB]]:
        """
        просто достать из базы товары
        """
        res = await OrdersRepository(self.db).find_all()
        return res

    async def create_order(self, product: ProductDB, user_id: int) -> SimpleResult[OrderDB]:
        """
        считаем, что за проверку "не пытается при покупке создать сто заказов"
        отвечает сервис покупки, а если уж дернули create_order, то это нам надо
        """
        order = OrderDB(
            orderId=str(user_id) + product.productId + datetime.now().strftime('%d%m%Y%H%M%S'), # todo: normal order id
            recipientId=user_id,  # tg_id
            productId=product.productId,
            price=product.price,
            title=product.title,
            photo=product.photo,
            orderStatus=OrderStatus.created,
        )
        order.created_at = order.updated_at = datetime.now(tz=timezone.utc)
        res = await OrdersRepository(self.db).insert(order)
        return res

    async def add_payment(self, order_id: str, payment_id: PyObjectId) -> SimpleResult[OrderDB]:
        """
        обязательный цикл заказа: мы его создаем, потом платим, потом добавляем оплату
        или отменяем по причине неоплаты
        привязываем исключительно успешные оплаты именно этого заказа!!
        здесь мы проверяем, что заказ есть и у него статус created, тогда добавляем оплату
        если статус неправильный или заказа нет, возвращаем ошибку/исключение??
        что возвращаем, надо поменять под нужды buying service
        """
        res = await OrdersRepository(self.db).order_by_order_id(order_id=order_id)
        if isinstance(res, SimpleErrorResult):
            return SimpleErrorResult(message=res.message)
        if res.payload.orderStatus != OrderStatus.created:
            return SimpleErrorResult(message="order wasn't in created state")

        payment_res = await ShopPaymentsRepository(db=self.db).get_by_id(object_id=payment_id)
        if isinstance(payment_res, SimpleErrorResult):
            return SimpleErrorResult(message=payment_res.message)
        if payment_res.payload.status != TransferStatus.completed:
            return SimpleErrorResult(message="wrong payment status")
        if payment_res.payload.orderId != order_id:
            return SimpleErrorResult(message="wrong payment orderId")

        order = res.payload
        order.updated_at = datetime.now(tz=timezone.utc)
        order.paymentId = str(payment_id)
        order.status = OrderStatus.paid
        result = await OrdersRepository(self.db).update_one(obj=order)
        if isinstance(result, SimpleErrorResult):
            return SimpleErrorResult(message=result.message)
        return SimpleOkResult(payload=order)

    async def order_set_cancelled(self, order_id: str,) -> SimpleResult[OrderDB]:
        """
        обязательный цикл заказа: мы его создаем, потом платим, потом добавляем оплату
        или отменяем по причине неоплаты
        привязываем исключительно успешные оплаты именно этого заказа!!
        здесь мы проверяем, что заказ есть и у него статус created, тогда добавляем оплату
        если статус неправильный или заказа нет, возвращаем ошибку/исключение??
        что возвращаем, надо поменять под нужды buying service
        """
        res = await OrdersRepository(self.db).order_by_order_id(order_id=order_id)
        if isinstance(res, SimpleErrorResult):
            return SimpleErrorResult(message=res.message)

        order = res.payload
        order.updated_at = datetime.now(tz=timezone.utc)
        order.status = OrderStatus.canceled
        result = await OrdersRepository(self.db).update_one(obj=order)
        if isinstance(result, SimpleErrorResult):
            return SimpleErrorResult(message=result.message)
        return SimpleOkResult(payload=order)

    # здесь могло бы быть "достань инфо о продукте по productId, но у нас нет инфо о продукте
    # и какие-то еще админовские круды
