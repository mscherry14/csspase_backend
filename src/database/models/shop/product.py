from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator, ConfigDict

from src.utils.validators import parse_date
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
    def parse_dates(cls, values):
        v_1 = parse_date('created_at', values=values)
        v_2 = parse_date('updated_at', values=v_1)
        return v_2

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )