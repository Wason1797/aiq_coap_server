from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRESQL_DB_HOST: str
    POSTGRESQL_DB_USER: str
    POSTGRESQL_DB_PASS: str
    POSTGRESQL_DB_PORT: str
    ENV: str = "DEV"

    model_config = SettingsConfigDict(env_file=".env")

    def get_db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRESQL_DB_USER}:{self.POSTGRESQL_DB_PASS}@{self.POSTGRESQL_DB_HOST}:{self.POSTGRESQL_DB_PORT}/sensordata"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
