import asyncio
from functools import partial

import aiocoap  # type: ignore
import aiocoap.resource as resource  # type: ignore

from app.config.env_manager import get_settings
from app.repositories.aiq_coap.client import CoapClient
from app.repositories.postgres.database import PostgresqlConnector
from app.repositories.postgres.managers import AiqDataManager
from app.resources import AiqDataResource
from app.telegram.bot import ManagementBot

EnvManager = get_settings()


async def main() -> None:
    PostgresqlConnector.init_db(EnvManager.get_db_url())
    ManagementBot.init_bot(EnvManager.BOT_TOKEN, EnvManager.get_allowed_users(), EnvManager.get_notification_user())
    ManagementBot.register_commad("summary", partial(AiqDataManager.get_summary, PostgresqlConnector.get_session))
    ManagementBot.register_commad("truncate", partial(AiqDataManager.truncate_db, PostgresqlConnector.get_session))

    coap_client = await CoapClient.get_instance(EnvManager.MAIN_SERVER_URI)

    server = resource.Site()
    server.add_resource(
        ["aiq-data"], AiqDataResource(EnvManager.should_forward(), EnvManager.LOCATION_ID, PostgresqlConnector.get_session, coap_client)
    )

    print("Starting AIQ Server")
    try:
        server_context = await aiocoap.Context.create_server_context(server)
        await ManagementBot.start_polling()

        await asyncio.get_running_loop().create_future()
    except (SystemExit, KeyboardInterrupt):
        print("Shutting Down")
        await server_context.shutdown()
        await ManagementBot.stop_polling()
        return


if __name__ == "__main__":
    asyncio.run(main())
