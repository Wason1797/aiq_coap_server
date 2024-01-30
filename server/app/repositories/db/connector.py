from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class BaseDBConnector:
    engine: Optional[AsyncEngine] = None
    sessionmaker: Any = None

    class Base(DeclarativeBase):
        pass

    @classmethod
    def init_db(cls, connection_str: str) -> None:
        if not cls.engine:
            cls.engine = create_async_engine(connection_str)

        if not cls.sessionmaker:
            cls.sessionmaker = async_sessionmaker(cls.engine, expire_on_commit=False)

    @classmethod
    def get_session(cls) -> AsyncSession:
        session = cls.sessionmaker()
        return session
