from pydantic import BaseModel


class TelegramAuthSchema(BaseModel):
    initData: str