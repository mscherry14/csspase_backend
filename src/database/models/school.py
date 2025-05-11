from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from pydantic_mongo import PydanticObjectId


class SchoolDB(BaseModel):
    id: Optional[PydanticObjectId] = Field(alias="_id")
    schoolId: str  # unique: true,
    title: str
    shortDescription: str
    dateStart: Optional[datetime] = None
    dateEnd: Optional[datetime] = None
    registrationDeadline: Optional[datetime] = None
    registrationLink: Optional[str] = None  # HttpUrl from pydantic
    tags: Optional[List[str]] = Field(default_factory=list)
    mainPage: Optional[bool] = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"collection": "schools"}
    )
