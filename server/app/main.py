import asyncio

import aiocoap  # type: ignore
import aiocoap.resource as resource  # type: ignore

from app.config.env_manager import get_settings
from app.repositories.postgres.database import PostgresqlConnector
from app.repositories.postgres.managers import AiqDataManager
from app.resources import AiqDataResource
from app.telegram.bot import ManagementBot
from functools import partial

EnvManager = get_settings()


async def main() -> None:
    PostgresqlConnector.init_db(EnvManager.get_db_url())
    ManagementBot.register_commad("summary", partial(AiqDataManager.get_summary, PostgresqlConnector.get_session()))

    server = resource.Site()

    server.add_resource(["aiq-data"], AiqDataResource())

    print("Starting AIQ Server")

    await aiocoap.Context.create_server_context(server)
    await ManagementBot.start_polling()

    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())
