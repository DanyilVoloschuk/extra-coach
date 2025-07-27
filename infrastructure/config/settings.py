
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    TELEGRAM_TOKEN: str = ""

    ADMIN_USERNAME: str = ""
    ADMIN_PASSWORD: str = ""

    VOICE_DIR: Path = Path("voice_messages")
    PHOTOS_DIR: Path = Path("photos")

    DATABASE_URL: str = "sqlite+aiosqlite:///./nutrition.db"

    HOST: str = "0.0.0.0"
    PORT: int = 80

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.VOICE_DIR.mkdir(parents=True, exist_ok=True)
        self.PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()