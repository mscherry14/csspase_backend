from pydantic import ConfigDict

from .event import EventModel


class ExtendedEventModel(EventModel):
    bankAccountId: str
    balance: int
    init_balance: int

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )