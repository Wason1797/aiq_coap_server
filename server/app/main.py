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
    ManagementBot.init_bot(EnvManager.BOT_TOKEN, EnvManager.get_allowed_users(), EnvManager.get_notification_user())
    ManagementBot.register_commad("summary", partial(AiqDataManager.get_summary, PostgresqlConnector.get_session))

    server = resource.Site()
    server.add_resource(["aiq-data"], AiqDataResource(EnvManager.LOCATION_ID, PostgresqlConnector.get_session))

    print("Starting AIQ Server")
    try:
        server_context = await aiocoap.Context.create_server_context(server)
        await ManagementBot.start_polling()

        await asyncio.get_running_loop().create_future()
    except KeyboardInterrupt:
        print("Shutting Down")
        await server_context.shutdown()
        await ManagementBot.stop_polling()
        return


if __name__ == "__main__":
    asyncio.run(main())
