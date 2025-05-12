from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from .utils import PyObjectId


class TeamDB(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    name: str
    members: List[str]  # List of user tg_ids
    captain_tg_id: int
    competition_id: str
    team_id: Optional[str] = None
    member_names: List[str] = Field(default_factory=list)  # List of member names
    yandex_id: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={"collection": "teams"}
    )