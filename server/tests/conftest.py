from typing import AsyncGenerator
from app.types import AsyncSessionMaker
import pytest_asyncio
from app.repositories.db.connector import BaseDBConnector


@pytest_asyncio.fixture(scope="function")
async def main_db_session() -> AsyncGenerator[AsyncSessionMaker, None]:
    BaseDBConnector.init_db("sqlite+aiosqlite:///:memory")

    assert BaseDBConnector.engine

    async with BaseDBConnector.engine.begin() as conn:
        await conn.run_sync(BaseDBConnector.Base.metadata.create_all)

        try:
            yield BaseDBConnector.get_session
        finally:
            await conn.run_sync(BaseDBConnector.Base.metadata.drop_all)


pytest_plugins = [
    "tests.fixtures.sensor_data",
]
