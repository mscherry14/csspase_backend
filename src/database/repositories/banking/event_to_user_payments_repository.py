from datetime import datetime, timezone
from typing import List

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection, AsyncIOMotorClientSession

from ...models import PyObjectId
from ...models.banking.utils import TransferStatus
from ....utils.simple_result import SimpleResult, SimpleErrorResult, SimpleOkResult
from ...models.banking.event_to_user_payment import EventToUserPaymentDB

COLLECTION = "eventToUserPayments"


class EventToUserPaymentsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    def get_collection(self) -> AsyncIOMotorCollection:
        return self.db[COLLECTION]

    async def create_payment(self, payment: EventToUserPaymentDB, session: AsyncIOMotorClientSession | None) -> SimpleResult[EventToUserPaymentDB]:
        """
        Порядок создания нового money transfer (возможно это делает скорее сервис, но и на уровне бд
        будем пытаться поддерживать на всякий:
        1. проверяем, есть ли активные money transfer операции у этого пользователя/аккаунта.
           Если есть, то отклоняем (пытаемся поддерживать инвариант: в один момент времени
           только одна операция покупки)
        3. возможно еще проверяем штуку "не начисляй одному и тому же, если полминуты не прошло"
        """
        unfinished_payment = await self.get_collection().find_one(
            {"fromEventBankingAccount": payment.fromEventBankingAccount, "status": TransferStatus.processing}, session=session)
        if not unfinished_payment:
            payment.id = None
            payment.status = TransferStatus.processing
            payment.created_at = payment.updated_at = datetime.now(tz=timezone.utc)
            try:
                result = await self.get_collection().insert_one(payment.model_dump(), session=session)
                if result.acknowledged:
                    payment.id = result.inserted_id
                    return SimpleOkResult(payload=payment)
                else:
                    return SimpleErrorResult(message=f"Unknown writing error:")
            except Exception as e:
                return SimpleErrorResult(message=str(e))
        else:
            return SimpleErrorResult(
                message=f"Cannot create payment: {EventToUserPaymentDB(**unfinished_payment)} in process")

    async def get_payments_by_filter(self, from_event_id: str | None, to_user_id: str | None,
                                     status: TransferStatus | None, session: AsyncIOMotorClientSession | None) -> SimpleResult[List[EventToUserPaymentDB]]:
        filter_opt = dict()
        if from_event_id:
            filter_opt["fromEventBankingAccount"] = from_event_id
        if to_user_id:
            filter_opt["toUserBankingAccount"] = to_user_id
        if status:
            filter_opt["status"] = status
        cursor = self.get_collection().find(filter_opt, session=session)
        try:
            payments = [EventToUserPaymentDB(**doc) async for doc in cursor]
            return SimpleOkResult(payload=payments)
        except Exception as e:
            return SimpleErrorResult(message="Payments parsing error: " + str(e))

    async def get_one_payment_by_filter(self, from_event_id: str | None, to_user_id: str | None,
                                        status: TransferStatus | None, session: AsyncIOMotorClientSession | None) -> SimpleResult[EventToUserPaymentDB]:
        filter_opt = dict()
        if from_event_id:
            filter_opt["fromEventBankingAccount"] = from_event_id
        if to_user_id:
            filter_opt["toUserBankingAccount"] = to_user_id
        if status:
            filter_opt["status"] = status
        payment = await self.get_collection().find_one(filter_opt, session=session)
        try:
            return SimpleOkResult(payload=EventToUserPaymentDB(**payment))
        except Exception as e:
            return SimpleErrorResult(message="Payments parsing error: " + str(e))

    async def change_payment_status(self, payment_id: PyObjectId, status: TransferStatus, session: AsyncIOMotorClientSession | None) -> SimpleResult[
        EventToUserPaymentDB]:
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
            payment = EventToUserPaymentDB(**doc)
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
