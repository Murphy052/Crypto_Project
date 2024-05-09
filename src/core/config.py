from datetime import timedelta
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_DIR: Any = Path(__file__).resolve().parent.parent

    # DB Params
    DB_PATH: str = "src/db/database.db"

    # JWT Params
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_LIFETIME: timedelta = timedelta(days=30)

    class Config:
        env_file = "./.env"
        extra = "ignore"


settings = Settings()
