import json
from typing import List, Optional, Literal, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, model_validator, Field, ConfigDict, AfterValidator

from .utils import TVideo, ExtraMaterial, SimmiliarEvent, strip_control_chars, PyObjectId
from ...utils.validators import parse_date


class CourseLectureDB(BaseModel):
    title: str
    description: str
    date: Optional[datetime] = None
    time: Optional[str] = None
    presentation: Optional[str] = None
    tags: Optional[List[str]] = None
    videos: Optional[List[TVideo]] = None
    speakers: List[EmailStr]

    @model_validator(mode='before')
    def v_parse_date(cls, values):
        date_value = values.get("date")
        if not date_value:
            values["date"] = None
            return values
        if isinstance(date_value, dict) and "$date" in date_value:
            date_value = date_value["$date"]
        if isinstance(date_value, str):
            values["date"] = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        return values


class CourseDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    courseId: str
    title: str
    description: str
    shortDescription: str
    year: str
    season: Literal["autumn", "spring"]
    extraMaterials: Optional[List[ExtraMaterial]] = None
    previewOnly: Optional[bool] = None
    tags: Optional[List[str]] = None
    lectures: Optional[List[CourseLectureDB]] = None
    speakers: Optional[List[EmailStr]] = None
    partnerLogos: Optional[List[str]] = None
    registrationLink: Optional[str] = None
    simmiliarEvents: Optional[List[SimmiliarEvent]] = None
    mainPage: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode="before")
    def clean_control_characters(cls, values: Any) -> Any:
        if isinstance(values, str):
            # если пришла сырая строка — чистим и парсим
            try:
                cleaned = strip_control_chars(values)
                values = json.loads(cleaned)
            except Exception as e:
                raise ValueError(f"Ошибка при очистке и парсинге JSON: {e}")

        elif isinstance(values, dict):
            # если dict — пробегаемся по строкам внутри
            for key, val in values.items():
                if isinstance(val, str):
                    values[key] = strip_control_chars(val)

        v_1 = parse_date('created_at', values=values)
        v_2 = parse_date('updated_at', values=v_1)
        return v_2

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"collection": "courses"}
    )
