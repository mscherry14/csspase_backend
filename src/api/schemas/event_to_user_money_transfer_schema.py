from typing import Literal

from pydantic import BaseModel
from pydantic_core.core_schema import LiteralSchema


class EventToUserMoneyTransferSchema(BaseModel):
    receiverName: str
    amount: int
    status: Literal["success", "failure"]