from pydantic import BaseModel


class UserSchema(BaseModel):
    id: str #????? maybe tg_id int
    name: str