from datetime import timedelta
from pathlib import Path
from typing import Any, List

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_DIR: Any = Path(__file__).resolve().parent.parent

    ALLOWED_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:8000",
        "https://yourdomain.com",
        "https://yourwebapp.net",
        "http://10.29.251.10:5500",
    ]

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
