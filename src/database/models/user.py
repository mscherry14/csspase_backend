from enum import Enum

from dotenv.variables import Literal
from pydantic import BaseModel, EmailStr, StringConstraints, Field, ConfigDict
from typing import Optional, List, Annotated

from .utils import PyObjectId

PhoneStr = Annotated[
    str,
    StringConstraints(
        pattern=r"^\+?\d{1,3}[\s-]?\(?\d{1,4}\)?[\s-]?\d{2,4}[\s-]?\d{2,4}[\s-]?\d{2,4}$"
    )
]

class UserRoles(str, Enum):
    USER = "user"
    TEACHER = "teacher"
    ADMIN = "admin"

class UserDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    tg_id: int
    mail: EmailStr
    name: str
    phone: PhoneStr
    position: str
    username: str
    workplace: str
    roles: List[UserRoles] = Field(default_factory=lambda: [UserRoles.USER])
    registered_lectures: List[str] = Field(default_factory=list)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"collection": "users"}
    )
