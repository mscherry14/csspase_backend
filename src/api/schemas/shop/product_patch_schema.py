from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProductPatchSchema(BaseModel):
    productId: Optional[str] = None
    price: Optional[int] = None
    title: Optional[str] = None
    photo: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
