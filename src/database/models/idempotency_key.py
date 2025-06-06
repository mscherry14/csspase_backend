from datetime import datetime
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field, model_validator, ConfigDict

from src.utils.validators import parse_date
from .utils import PyObjectId


class IdempotencyStatus(str, Enum):
    PENDING = "pending"
    DONE = "done"
    FAILED = "failed"

class IdempotencyKeyDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    key: str
    status: IdempotencyStatus
    status_code: int = Field(..., alias="statusCode")
    response: Any
    expires_at: datetime

    @model_validator(mode='before')
    def parse_dates(cls, values):
        v_1 = parse_date('expires_at', values=values)
        return v_1

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
