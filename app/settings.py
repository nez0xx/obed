from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path


BASE_DIR = Path(__file__).parent.parent
DOTENV = os.path.join(BASE_DIR, ".env")


class SettingsWithLoadEnvVars(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=DOTENV,
        env_file_encoding='utf-8',
        extra='ignore'
    )


class Settings(SettingsWithLoadEnvVars):
    BOT_TOKEN: str
    DB_URL: str
    BOT_LINK: str


settings = Settings()
