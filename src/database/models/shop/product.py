from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict

from ..utils import PyObjectId

class ProductDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    productId: str
    price: int
    title: str
    photo: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @model_validator(mode='before')
    def parse_date(cls, values):
        date_value = values.get("date")
        if isinstance(date_value, dict) and "$date" in date_value:
            date_value = date_value["$date"]
        if isinstance(date_value, str):
            if not date_value.strip():
                return None
            values["date"] = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
        return values

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )