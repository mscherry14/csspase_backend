from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict

from src.utils.validators import parse_date
from ..utils import PyObjectId


class OrderStatus(str, Enum):
    created = "created"
    paid = "paid"
    confirmed = "confirmed"
    canceled = "canceled"
    # waiting = "waiting"
    completed = "completed"


class OrderDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    orderId: str
    recipientId: int  # tg_id
    productId: str  # reference to product id. can be dirty bc of product deleting
    # copy of product == order list
    price: int
    title: str
    photo: Optional[str] = None  # can be dirty
    orderStatus: OrderStatus
    paymentId: Optional[str] = None  # str(objid) of payment, invariants: payment = None or
    # payment with SUCCESS status, if none then order status created, can be modified if not None, if not
    # none then can't be unpayed(created) status
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode='before')
    def parse_dates(cls, values):
        v_1 = parse_date('created_at', values=values)
        v_2 = parse_date('updated_at', values=v_1)
        return v_2

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
