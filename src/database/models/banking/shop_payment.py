from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, model_validator, ConfigDict

from ..utils import PyObjectId
from .utils import TransferStatus

class ShopPaymentDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    fromUserBankingAccount: str # USE ACCOUNT ID instead of using tg_id (one user = one account)
    toShopAccount: Literal["cs_space_banking_account"] = "cs_space_banking_account"
    amount: int
    orderId: str
    status: TransferStatus = Field(TransferStatus.processing)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

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