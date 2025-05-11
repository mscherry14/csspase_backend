from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, ConfigDict

from .utils import PyObjectId


class CompetitionDB(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    competitionId: str  # unique
    title: str
    shortDescription: str
    dateStart: Optional[datetime] = None
    dateEnd: Optional[datetime] = None
    registrationDeadline: Optional[datetime] = None
    registrationLink: Optional[str] = None
    tags: Optional[List[str]] = None
    mainPage: Optional[bool] = None
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
        json_schema_extra={"collection": "competitions"}
    )

