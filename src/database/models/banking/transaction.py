from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import model_validator, Field, ConfigDict, BaseModel

from src.utils.validators import parse_date
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
    def parse_dates(cls, values):
        v_1 = parse_date('created_at', values=values)
        return v_1

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )