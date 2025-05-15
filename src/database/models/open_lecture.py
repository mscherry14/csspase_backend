from pydantic import BaseModel, EmailStr, model_validator, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from .utils import ExtraMaterial, TVideo, SimmiliarEvent, PyObjectId


class OpenLectureDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    openLectureId: str  # unique
    title: str
    description: str
    shortDescription: str
    extraMaterials: Optional[List[ExtraMaterial]] = None
    date: Optional[datetime] = None  # required but cant be empty
    time: Optional[str] = ""  # required but cant be empty
    previewOnly: Optional[bool] = False  # ask about
    tags: Optional[List[str]] = Field(default_factory=list)
    presentation: Optional[str] = None
    videos: Optional[List[TVideo]] = Field(default_factory=list)
    speakers: Optional[List[EmailStr]] = Field(default_factory=list)  # check for null??
    partnerLogos: Optional[List[str]] = Field(default_factory=list)
    registrationLink: Optional[str] = None
    simmiliarEvents: Optional[List[SimmiliarEvent]] = None
    mainPage: Optional[bool] = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode='before')
    def parse_date(cls, values):
        date_value = values.get("date")
        if not date_value:
            values["date"] = None
            return values
        if isinstance(date_value, dict) and "$date" in date_value:
            date_value = date_value["$date"]
        if isinstance(date_value, str):
            values["date"] = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        return values

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"collection": "openLectures"}
    )
