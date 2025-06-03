from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, model_validator

from .event import EventModel
from ...utils.validators import parse_date


class ExtendedEventModel(EventModel):
    bankAccountId: str
    balance: int
    init_balance: int
    bankAccountDeadline: Optional[datetime] = None

    @model_validator(mode='before')
    def parse_dates(cls, values):
        v_1 = parse_date('bankAccountDeadline', values=values)
        return v_1


    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )