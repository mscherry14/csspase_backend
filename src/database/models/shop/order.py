from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict

from ..utils import PyObjectId

class OrderStatus(str, Enum):
    created = "created"
    confirmed = "confirmed"
    canceled = "canceled"
    # waiting = "waiting"
    completed = "completed"

class OrderDB(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    orderId: str
    recipientId: int # tg_id
    productId: str # reference to product id. can be dirty bc of product deleting
    # copy of product == order list
    price: int
    title: str
    photo: Optional[str] = None # can be dirty
    orderStatus: OrderStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode='before')
    def parse_date(cls, values):
        date_value = values.get("date")
        if isinstance(date_value, dict) and "$date" in date_value:
            date_value = date_value["$date"]
        if isinstance(date_value, str):
            values["date"] = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        return values

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )