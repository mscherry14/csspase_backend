from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, model_validator, ConfigDict

from src.utils.validators import parse_date
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
    def parse_dates(cls, values):
        v_1 = parse_date('created_at', values=values)
        v_2 = parse_date('updated_at', values=v_1)
        return v_2

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )