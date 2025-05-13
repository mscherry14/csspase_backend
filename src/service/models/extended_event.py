from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, model_validator, ConfigDict

from .event import EventType
from ...database.models import PyObjectId, OpenLectureDB, CourseDB, CompetitionDB, SchoolDB


class ExtendedEventModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    eventId: str
    title: str
    type: EventType
    shortDescription: str
    speakers: List[EmailStr] = Field(default=list)
    tags: Optional[List[str]] = None
    registrationDeadline: Optional[datetime] = None
    registrationLink: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    bankAccountId: str
    balance: int
    init_balance: int

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
    )