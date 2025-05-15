from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator, ConfigDict

from src.service.models.event import EventType
from src.service.models.extended_event import ExtendedEventModel
from src.utils.validators import parse_date


class EventShortSchema(BaseModel):
    eventId: str
    title: str
    type: EventType
    shortDescription: str
    tags: Optional[List[str]] = None
    dateTags: Optional[List[str]] = None
    registrationDeadline: Optional[datetime] = None
    registrationLink: Optional[str] = None
    balance: int
    init_balance: int

    @model_validator(mode='before')
    def parse_dates(cls, values):
        v_1 = parse_date('registration_deadline', values=values)
        return v_1


    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    @staticmethod
    def from_extended_event(event: ExtendedEventModel) -> "EventShortSchema":
        return EventShortSchema(
            eventId=event.eventId,
            title=event.title,
            type=event.type,
            shortDescription=event.shortDescription,
            tags=event.tags,
            dateTags=event.dateTags,
            registrationDeadline=event.registrationDeadline,
            registrationLink=event.registrationLink,
            balance=event.balance,
            init_balance=event.init_balance,
        )
