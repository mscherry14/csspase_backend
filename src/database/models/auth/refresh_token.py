from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator, ConfigDict

from src.utils.validators import parse_date
from ..utils import PyObjectId


class RefreshTokenDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: int = Field(..., alias="userId")
    token_hash: str = Field(..., alias="tokenHash")
    expires_at: datetime

    @model_validator(mode='before')
    def parse_dates(cls, values):
        v_1 = parse_date('expires_at', values=values)
        return v_1

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"collection": "eventBankingAccounts"},
    )
