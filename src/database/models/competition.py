from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, ConfigDict, EmailStr

from .utils import PyObjectId
from ...utils.validators import parse_date


class CompetitionDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    competitionId: str  # unique
    title: str
    shortDescription: str
    dateStart: Optional[datetime] = None
    dateEnd: Optional[datetime] = None
    speakers: Optional[List[EmailStr]] = None
    registrationDeadline: Optional[datetime] = None
    registrationLink: Optional[str] = None
    tags: Optional[List[str]] = None
    mainPage: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode='before')
    def parse_dates(cls, values):
        v_1 = parse_date('created_at', values=values)
        v_2 = parse_date('updated_at', values=v_1)
        v_3 = parse_date('registration_deadline', values=v_2)
        v_4 = parse_date('dateStart', values=v_3)
        v_5 = parse_date('dateEnd', values=v_4)
        return v_5

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"collection": "competitions"}
    )

