from typing import AsyncGenerator
from app.types import AsyncSessionMaker
import pytest_asyncio
from app.repositories.db.connector import BaseDBConnector


@pytest_asyncio.fixture(scope="function")
async def main_db_session() -> AsyncGenerator[AsyncSessionMaker, None]:
    class TestDBConnector(BaseDBConnector):
        pass

    TestDBConnector.init_db("sqlite+aiosqlite:///:main_test_db")

    assert TestDBConnector.engine

    async with TestDBConnector.engine.begin() as conn:
        await conn.run_sync(TestDBConnector.Base.metadata.create_all)

        try:
            yield TestDBConnector.get_session
        finally:
            await conn.run_sync(TestDBConnector.Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def backup_db_session() -> AsyncGenerator[AsyncSessionMaker, None]:
    class TestBackupDBConnector(BaseDBConnector):
        pass

    TestBackupDBConnector.init_db("sqlite+aiosqlite:///:backup_test_db")

    assert TestBackupDBConnector.engine

    async with TestBackupDBConnector.engine.begin() as conn:
        await conn.run_sync(TestBackupDBConnector.Base.metadata.create_all)

        try:
            yield TestBackupDBConnector.get_session
        finally:
            await conn.run_sync(TestBackupDBConnector.Base.metadata.drop_all)


pytest_plugins = [
    "tests.fixtures.sensor_data",
    "tests.fixtures.br_data",
    "tests.fixtures.aiq_data",
    "tests.fixtures.payload_validator",
    "tests.fixtures.management_bot",
    "tests.fixtures.coap_client",
]
