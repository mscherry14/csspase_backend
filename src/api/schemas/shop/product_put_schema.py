from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProductPutSchema(BaseModel):
    price: int
    title: str
    photo: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
