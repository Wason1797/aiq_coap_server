from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncEngine

from app.repositories.db.connector import BaseDBConnector


class PostgresqlConnector(BaseDBConnector):
    engine: Optional[AsyncEngine] = None
    sessionmaker: Any = None
