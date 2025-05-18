from datetime import datetime, timezone
from typing import List

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection, AsyncIOMotorClientSession

from ...models import PyObjectId
from ...models.banking.utils import TransferStatus
from ....utils.simple_result import SimpleResult, SimpleErrorResult, SimpleOkResult
from ...models.banking.shop_payment import ShopPaymentDB

COLLECTION = "shopPayments"


class ShopPaymentsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    def get_collection(self) -> AsyncIOMotorCollection:
        return self.db[COLLECTION]

    async def create_payment(self, payment: ShopPaymentDB, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[ShopPaymentDB]:
        """
        Порядок создания нового money transfer (возможно это делает скорее сервис, но и на уровне бд
        будем пытаться поддерживать на всякий:
        1. проверяем, есть ли активные money transfer операции у этого пользователя/аккаунта.
           Если есть, то отклоняем (пытаемся поддерживать инвариант: в один момент времени
           только одна операция покупки)
        2. проверяем orderId
        3. возможно еще проверяем штуку "не начисляй одному и тому же, если полминуты не прошло"
        """
        unfinished_payment = await self.get_collection().find_one(
            {"fromUserBankingAccount": payment.fromUserBankingAccount,
             "status": TransferStatus.processing}, session=session) or await self.get_collection().find_one(
            {"orderId": payment.orderId, "status": TransferStatus.processing}, session=session) or await self.get_collection().find_one(
            {"orderId": payment.orderId, "status": TransferStatus.completed}, session=session)
        if not unfinished_payment:
            payment.id = None
            payment.status = TransferStatus.processing
            payment.created_at = payment.updated_at = datetime.now(tz=timezone.utc)
            try:
                result = await self.get_collection().insert_one(payment.model_dump(exclude_unset=True, exclude_none=True), session=session)
                if result.acknowledged:
                    payment.id = result.inserted_id
                    return SimpleOkResult(payload=payment)
                else:
                    return SimpleErrorResult(message=f"Unknown writing error:")
            except Exception as e:
                return SimpleErrorResult(message=str(e))
        else:
            return SimpleErrorResult(
                message=f"Cannot create payment: {ShopPaymentDB(**unfinished_payment)} in process or payment already completed")

    async def get_payments_by_filter(self, from_user_id: str | None, order_id: str | None,
                                     status: TransferStatus | None, session: AsyncIOMotorClientSession | None = None
                                     ) -> SimpleResult[List[ShopPaymentDB]]:
        filter_opt = dict()
        if from_user_id:
            filter_opt["fromUserBankingAccount"] = from_user_id
        if order_id:
            filter_opt["orderId"] = status
        if status:
            filter_opt["status"] = status
        cursor = self.get_collection().find(filter_opt, session=session)
        try:
            payments = [ShopPaymentDB(**doc) async for doc in cursor]
            return SimpleOkResult(payload=payments)
        except Exception as e:
            return SimpleErrorResult(message="Payments parsing error: " + str(e))

    async def get_one_payment_by_filter(self, from_user_id: str | None, order_id: str | None,
                                        status: TransferStatus | None, session: AsyncIOMotorClientSession | None = None
                                        ) -> SimpleResult[ShopPaymentDB]:
        filter_opt = dict()
        if from_user_id:
            filter_opt["fromUserBankingAccount"] = from_user_id
        if order_id:
            filter_opt["orderId"] = status
        if status:
            filter_opt["status"] = status
        payment = await self.get_collection().find_one(filter_opt, session=session)
        try:
            return SimpleOkResult(payload=ShopPaymentDB(**payment))
        except Exception as e:
            return SimpleErrorResult(message="Payments parsing error: " + str(e))

    async def get_one_by_id(self, object_id: PyObjectId, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[ShopPaymentDB]:
        try:
            object_id = ObjectId(object_id)
            doc = await self.get_collection().find_one({"_id": object_id}, session=session)
            if not doc:
                return SimpleErrorResult(f"Document with id={object_id} not found")
            return SimpleOkResult(payload=ShopPaymentDB(**doc))
        except Exception as e:
            return SimpleErrorResult(str(e))

    async def change_payment_status(self, payment_id: PyObjectId, status: TransferStatus, session: AsyncIOMotorClientSession | None = None) -> SimpleResult[
        ShopPaymentDB]:
        if status == TransferStatus.processing:
            return SimpleErrorResult(message="You can't set processing payment status")
        try:
            obj_id = ObjectId(payment_id)
        except InvalidId:
            return SimpleErrorResult(message="Invalid payment id")
        doc = await self.get_collection().find_one({"_id": obj_id}, session=session)
        if not doc:
            return SimpleErrorResult(message="Payment not found")
        else:
            payment = ShopPaymentDB(**doc)
            if payment.status == TransferStatus.processing:
                res = await self.get_collection().update_one(filter={"_id": obj_id},
                                                             update={"$set": {"status": status}}, session=session)
                if res.acknowledged:
                    return SimpleOkResult(payload=payment)
                else:
                    return SimpleErrorResult(message=f"Unknown writing error.")
            else:
                return SimpleErrorResult(
                    message=f"Cannot change payment status: payment status is not processing ({payment.status}), so it cant be changed")
