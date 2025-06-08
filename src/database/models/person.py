from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from .utils import PyObjectId


class PersonDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    tg_id: Optional[int] = None
    firstName: str
    lastName: str
    bio: str
    role: str
    photo: str
    email: EmailStr
    priority: Optional[int | str] = None
    mainPage: Optional[bool] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"collection": "users"}
    )
