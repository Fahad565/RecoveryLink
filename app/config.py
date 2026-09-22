from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "RecoveryLink"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000

    AT_USERNAME: str = "sandbox"
    AT_API_KEY: str = "sandbox_key"
    AT_SENDER_ID: Optional[str] = "RecoveryLink"

    DATABASE_URL: str = "sqlite:///./recoverylink.db"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
