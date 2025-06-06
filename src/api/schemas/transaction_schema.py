from datetime import datetime
from typing import Optional
from pydantic import BaseModel, model_validator, ConfigDict

from src.database.database import db
from src.database.models import PyObjectId
from src.database.models.banking.transaction import TransactionType, TransactionDB
from src.database.repositories.banking.event_banking_accounts_repository import EventBankingAccountsRepository
from src.database.repositories.banking.event_to_user_payments_repository import EventToUserPaymentsRepository
from src.database.repositories.banking.shop_payments_repository import ShopPaymentsRepository
from src.database.repositories.shop.orders_repository import OrdersRepository
from src.service.event_service import EventService
from src.utils.simple_result import SimpleErrorResult
from src.utils.validators import parse_date


class TransactionSchema(BaseModel):
    headline: str
    amount: int
    created_at: Optional[datetime] = None

    @model_validator(mode='before')
    def parse_dates(cls, values):
        v_1 = parse_date('created_at', values=values)
        return v_1

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    @staticmethod
    async def users_from_transaction_db(trans: TransactionDB) -> "TransactionSchema":
        headline = ""
        res = await EventToUserPaymentsRepository(db=db).get_one_by_id(operation_id=trans.operation_id)
        if isinstance(res, SimpleErrorResult):
            res = await ShopPaymentsRepository(db=db).get_one_by_id(object_id=PyObjectId(trans.operation_id))
            if isinstance(res, SimpleErrorResult):
                raise Exception("transaction not found")
            order = await OrdersRepository(db=db).order_by_order_id(res.payload.orderId)
            if isinstance(order, SimpleErrorResult):
                raise Exception("order for transaction not found")
            headline = "Покупка в магазине: " + order.payload.title
        else:
            event_acc = await EventBankingAccountsRepository(db=db).get_account_by_account_id(res.payload.fromEventBankingAccount)
            if isinstance(event_acc, SimpleErrorResult):
                raise Exception("event for transaction not found")
            event = await EventService(db=db).get_event_by_id(event_id=event_acc.payload.event)
            headline = "Начисление за мероприятие: " + event.title


        return TransactionSchema(
            headline=headline,
            amount=trans.amount if trans.type == TransactionType.deposit else -trans.amount,
            created_at=trans.created_at,
        )