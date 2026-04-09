import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Behavior-Based Manipulation Scoring API"
    sqlite_url: str = os.getenv("SQLITE_URL", "sqlite:///./manipulation.db")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
