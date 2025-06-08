from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from src.database.models import PyObjectId

#TODO: refactor if needed
class PersonModel(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    tg_id: Optional[int] = None
    firstName: str
    lastName: str
    role: str
    photo: str
    email: EmailStr

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"collection": "eventBankingAccounts"},
    )