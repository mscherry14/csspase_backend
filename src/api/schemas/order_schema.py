from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, model_validator, BaseModel

from src.database.models.shop.order import OrderStatus


class OrderSchema(BaseModel):
    orderId: str
    price: int
    title: str
    photo: Optional[str] = None
    orderStatus: OrderStatus
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
