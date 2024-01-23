import asyncio
import aiocoap.resource as resource
import aiocoap

from app.resources import AiqDataResource
from app.repositories.postgres.database import PostgresqlConnector
from app.config.env_manager import get_settings

EnvManager = get_settings()


async def main() -> None:
    PostgresqlConnector.init_db(EnvManager.get_db_url())

    server = resource.Site()

    server.add_resource(["aiq-data"], AiqDataResource())

    print("Server ready!")

    await aiocoap.Context.create_server_context(server)
    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())
