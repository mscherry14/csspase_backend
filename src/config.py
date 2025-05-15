from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URL: str = Field(default="mongodb://mongo:27017")
    MONGO_NAME: str = Field(default="test")
    TELEGRAM_TOKEN: str

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()
