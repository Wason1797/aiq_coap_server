from enum import StrEnum
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class StationType(StrEnum):
    BORDER_ROUTER = "BORDER_ROUTER"
    MAIN_SERVER = "MAIN_SERVER"


class ReplicationType(StrEnum):
    # Messages to the main server come from a replica server in the border router
    # device -> br -> br_server -> main_server
    FROM_BORDER_ROUTER = "FROM_BORDER_ROUTER"
    # Messages to the main server come from the end device directly
    # device -> br -> main_server
    NONE = "NONE"


class Settings(BaseSettings):
    POSTGRESQL_DB_URL: str
    MYSQL_DB_URL: str
    ALLOWED_BOT_USERS: str
    BOT_TOKEN: str
    SECRET_KEY: str
    STATION_TYPE: StationType
    VERSION: str
    ENV: str = "DEV"
    SEVRER_INSTANCE_ID: int
    REPLICATION: ReplicationType = ReplicationType.NONE
    WRITE_TO_BACKUP: bool = True
    MAIN_SERVER_URI: Optional[str] = None
    BIND: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")

    def get_main_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRESQL_DB_URL}/sensordata"

    def get_backup_db_url(self) -> str:
        return f"mysql+asyncmy://{self.MYSQL_DB_URL}/sensordata?charset=utf8mb4"

    def get_allowed_users(self) -> list[int]:
        return [int(id) for id in self.ALLOWED_BOT_USERS.split(",")]

    def get_notification_user(self) -> int:
        return self.get_allowed_users()[0]

    def should_forward(self) -> bool:
        return bool(self.MAIN_SERVER_URI)

    def is_main_server(self) -> bool:
        return self.STATION_TYPE == StationType.MAIN_SERVER

    def is_dev(self) -> bool:
        return self.ENV.upper() == "DEV"

    def allow_messages_from_br(self) -> bool:
        return self.REPLICATION == ReplicationType.FROM_BORDER_ROUTER

    def allow_backups(self) -> bool:
        return self.WRITE_TO_BACKUP and bool(self.get_backup_db_url())


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
