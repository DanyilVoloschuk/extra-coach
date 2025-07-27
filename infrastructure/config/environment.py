from pathlib import Path
from infrastructure.config.settings import get_settings

settings = get_settings()


def initialize_environment() -> None:
    settings.VOICE_DIR.mkdir(exist_ok=True)
