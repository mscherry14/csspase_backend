from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase

from .money_transfer_service import MoneyTransferService
from .orders_service import OrdersService
from ..database.models.banking.shop_payment import ShopPaymentDB
from ..database.models.banking.utils import TransferStatus
from ..database.models.shop.order import OrderDB
from ..database.models.shop.product import ProductDB
from ..database.repositories.banking.shop_payments_repository import ShopPaymentsRepository
from ..database.repositories.banking.user_banking_accounts_repository import UserBankingAccountsRepository
from ..database.repositories.shop.products_repository import ProductsRepository
from ..database.repositories.users_repository import UsersRepository
from ..utils.simple_result import SimpleResult, SimpleErrorResult, SimpleOkResult


class ShopService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_products_list(self) -> SimpleResult[List[ProductDB]]:
        """
        просто достать из базы товары
        """
        res = await ProductsRepository(self.db).find_all()
        return res

    # здесь могло бы быть "достань инфо о продукте по productId, но у нас нет инфо о продукте
    # и какие-то еще админовские круды

    async def buy_product(self, user_id: int, product_id: str) -> SimpleResult[OrderDB]:
        """
        Процесс покупки:
        1. проверяем существование продукта
        2. проверяем существование пользователя
        3.0 достаем из широких штанин userbankingaccount
        3. проверка "не пытается при покупке создать сто заказов" -- (??)
        4. создаем заказ
        5. создаем shop payment обязательство (проверки?)
        6. пушим create shop payment
            Тут уже делается в бд-левел следующее:
                Порядок создания нового money transfer (возможно это делает скорее сервис, но и на уровне бд
                будем пытаться поддерживать на всякий):
                1. проверяем, есть ли активные money transfer операции у этого пользователя/аккаунта.
                    Если есть, то отклоняем (пытаемся поддерживать инвариант: в один момент времени
                    только одна операция покупки)
                2. проверяем orderId
                3. возможно еще проверяем штуку "не начисляй одному и тому же, если полминуты не прошло"
        6.1 (и добавляем в order, если не позже)
        7. money transfer session с shop payment
        8. меняем статус shop payment в соответствие с результатом money transfer
           (возможно внутри money transfer)
        9. меняем статус order в соответствие с результатом (и добавляем payment, если не раньше)
        """
        async with await self.db.client.start_session() as session:
            try:
                async with session.start_transaction():
                    # step 1 product
                    res = await ProductsRepository(db=self.db).product_by_product_id(product_id=product_id, session=session)
                    if isinstance(res, SimpleErrorResult):
                        return SimpleErrorResult(message='Products doesnt exist')
                    product = res.payload
                    # step 2 user
                    res = await UsersRepository(db=self.db).get_by_user_id(user_id=user_id, session=session)
                    if isinstance(res, SimpleErrorResult):
                        return SimpleErrorResult(message='User doesnt exist')
                    # step 3 ?
                    # step 3.0 get user banking account
                    res = await UserBankingAccountsRepository(db=self.db).get_account_by_user_id(user_id=user_id, session=session)
                    if isinstance(res, SimpleErrorResult):
                        return SimpleErrorResult(message='User banking account error: ' + res.message)
                    user_banking_account_id = res.payload.accountId
                    # step 4 create order
                    res = await OrdersService(db=self.db).create_order(product=product, user_id=user_id, session=session)
                    if isinstance(res, SimpleErrorResult):
                        return SimpleErrorResult(message=res.message)
                    order = res.payload
                    # step 5 shop payment
                    shop_payment = ShopPaymentDB(
                        fromUserBankingAccount=user_banking_account_id,
                        amount=product.price,
                        orderId=order.orderId,
                        status=TransferStatus.processing,
                    )
                    # step 6 push shop payment
                    res = await ShopPaymentsRepository(db=self.db).create_payment(payment=shop_payment, session=session)
                    if isinstance(res, SimpleErrorResult):
                        return SimpleErrorResult(message="shop payment creating error:" + res.message)
                    shop_payment = res.payload

                    # step 7 money transfer
                    await MoneyTransferService(db=self.db).shop_transfer_money(session=session,
                                                                               from_acc=shop_payment.fromUserBankingAccount,
                                                                               to_acc=shop_payment.toShopAccount,
                                                                               amount=shop_payment.amount,
                                                                               operation_id=str(shop_payment.id),)

                    # step 8 set shop payment status
                    # step 9 set order status
                    inner_res = await ShopPaymentsRepository(db=self.db).change_payment_status(
                        payment_id=shop_payment.payment_id,
                        status=TransferStatus.completed, session=session)
                    if isinstance(inner_res, SimpleErrorResult):
                        raise Exception(inner_res.message)
                    inner_res = await OrdersService(db=self.db).add_payment(order_id=order.orderId,
                                                                            payment_id=shop_payment.payment_id, session=session)
                    if isinstance(inner_res, SimpleErrorResult):
                        raise Exception(inner_res.message)

                    # если всё ок → commit
            except Exception as e:
                return SimpleErrorResult(message=str("Transaction failed: " + str(e)))

        return SimpleOkResult(payload=inner_res.payload)