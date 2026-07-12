from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    DATABASE_URL: str = "sqlite:///./blog.db"

    secret_key: SecretStr

    algorithm: str = "HS256"

    access_token_expire_minutes: int = 30

    max_upload_size_bytes: int = 5*1024*1024

settings = Settings()
DATABASE_URL = settings.DATABASE_URL