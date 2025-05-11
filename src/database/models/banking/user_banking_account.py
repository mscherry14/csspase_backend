from datetime import datetime
from typing import Optional, List

from pydantic import model_validator, Field, ConfigDict, BaseModel

from ..utils import PyObjectId
from .transaction import TransactionDB


class UserBankingAccountDB(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    accountId: str
    balance: int
    owner: int
    transactions: List[TransactionDB] = Field(default_factory=list)
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
        json_schema_extra={"collection": "userBankingAccounts"}
    )