from datetime import datetime
from typing import Optional, List

from pydantic import model_validator, Field, ConfigDict, BaseModel

from src.utils.validators import parse_date
from .transaction import TransactionDB
from ..utils import PyObjectId


class EventBankingAccountDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    accountId: str
    balance: int
    init_balance: int
    event: str
    transactions: List[TransactionDB] = Field(default_factory=list)
    deadline: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode='before')
    def parse_dates(cls, values):
        v_1 = parse_date('created_at', values=values)
        v_2 = parse_date('updated_at', values=v_1)
        v_3 = parse_date('deadline', values=v_2)
        return v_3

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"collection": "eventBankingAccounts"},
    )
