from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str
    MONGODB_NAME: str
    ORIGIN: str
    TELEGRAM_TOKEN: str

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }

settings = Settings()
