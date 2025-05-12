from pydantic import BaseModel


class TelegramAuthSchema(BaseModel):
    init_data: str