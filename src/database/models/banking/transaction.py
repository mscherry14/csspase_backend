from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import model_validator, Field, ConfigDict, BaseModel

from ..utils import PyObjectId

class TransactionType(str, Enum):
    deposit = "deposit"
    withdraw = "withdraw"

class TransactionDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    amount: int
    type: TransactionType
    operation_id: str # it is shop payment/event-to-user payment objectid to string???
    created_at: Optional[datetime] = None

    @model_validator(mode='before')
    def parse_date(cls, values):
        date_value = values.get("date")
        if isinstance(date_value, dict) and "$date" in date_value:
            date_value = date_value["$date"]
        if isinstance(date_value, str):
            if not date_value.strip():
                return None
            values["date"] = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        return values

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )