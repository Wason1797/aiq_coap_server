from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRESQL_DB_HOST: str
    POSTGRESQL_DB_USER: str
    POSTGRESQL_DB_PASS: str
    POSTGRESQL_DB_PORT: str
    ALLOWED_BOT_USERS: str
    BOT_TOKEN: str
    LOCATION_ID: str = "default"
    ENV: str = "DEV"

    model_config = SettingsConfigDict(env_file=".env")

    def get_db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRESQL_DB_USER}:{self.POSTGRESQL_DB_PASS}@{self.POSTGRESQL_DB_HOST}:{self.POSTGRESQL_DB_PORT}/sensordata"
        )

    def get_allowed_users(self) -> list[int]:
        return [int(id) for id in self.ALLOWED_BOT_USERS.split(",")]

    def get_notification_user(self) -> int:
        return self.get_allowed_users()[0]


@lru_cache
def get_settings() -> Settings:
    return Settings()
