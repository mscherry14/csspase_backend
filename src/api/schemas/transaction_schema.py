from datetime import datetime
from typing import Optional
from pydantic import BaseModel, model_validator, ConfigDict

from src.database.models.banking.transaction import TransactionType
from src.utils.validators import parse_date


class TransactionSchema(BaseModel):
    amount: int
    type: TransactionType
    created_at: Optional[datetime] = None

    @model_validator(mode='before')
    def parse_dates(cls, values):
        v_1 = parse_date('created_at', values=values)
        return v_1

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )