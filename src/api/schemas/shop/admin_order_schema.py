from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, model_validator, BaseModel

from src.database.models.shop.order import OrderStatus
from src.utils.validators import parse_date


class AdminOrderSchema(BaseModel):
    orderId: str
    recipientId: int
    productId: str
    price: int
    title: str
    photo: Optional[str] = None
    orderStatus: OrderStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode='before')
    def parse_dates(cls, values):
        v_1 = parse_date('updated_at', values=values)
        return v_1

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
