"""Configuración centralizada del sistema. Lee las variables del archivo .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Telegram ---
    TELEGRAM_BOT_TOKEN: str

    # --- Base de datos ---
    DATABASE_URL: str

    # --- Aplicación ---
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    TIMEZONE: str = "America/Guayaquil"
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Investigación / ética ---
    ANON_SALT: str

    # --- Seguridad / JWT ---
    JWT_SECRET: str
    JWT_EXPIRE_HOURS: int = 8

    # --- Knowledge Tracing ---
    SAKT_CHECKPOINT: str | None = None

    @property
    def is_dev(self) -> bool:
        return self.ENV == "development"


settings = Settings()