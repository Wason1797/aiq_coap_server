import asyncio
from functools import partial

import aiocoap  # type: ignore
import aiocoap.resource as resource  # type: ignore

from app.config.env_manager import get_settings
from app.managers.aiq_manager import AiqDataManager
from app.repositories.aiq_coap.client import CoapClient
from app.repositories.postgres.database import PostgresqlConnector
from app.repositories.mysql.database import MysqlConnector
from app.resources import AiqDataResource, AiqManagementTruncateResource, AiqManagementSummaryResource
from app.telegram.bot import ManagementBot

EnvManager = get_settings()


async def main() -> None:
    PostgresqlConnector.init_db(EnvManager.get_main_db_url())
    MysqlConnector.init_db(EnvManager.get_backup_db_url())
    ManagementBot.init_bot(EnvManager.BOT_TOKEN, EnvManager.get_allowed_users(), EnvManager.get_notification_user())
    ManagementBot.register_commad("summary", partial(AiqDataManager.get_summary, PostgresqlConnector.get_session))
    # ManagementBot.register_commad("truncate", partial(, PostgresqlConnector.get_session))

    coap_client = await CoapClient.get_instance(EnvManager.MAIN_SERVER_URI)

    server = resource.Site()
    server.add_resource(
        ["aiq-data"],
        AiqDataResource(
            EnvManager.is_main_server(), EnvManager.LOCATION_ID, PostgresqlConnector.get_session, MysqlConnector.get_session, coap_client
        ),
    )

    if not EnvManager.is_main_server():  # Enable management interface for border routers
        server.add_resource(["aiq-management", "summary"], AiqManagementSummaryResource(EnvManager.LOCATION_ID, PostgresqlConnector.get_session))
        server.add_resource(["aiq-management", "truncate"], AiqManagementTruncateResource(EnvManager.LOCATION_ID, PostgresqlConnector.get_session))

    print("Starting AIQ Server")
    try:
        binds = ("localhost", None) if EnvManager.is_dev() else None
        server_context = await aiocoap.Context.create_server_context(server, bind=binds)

        if EnvManager.is_main_server():  # Only one instance of the bot can run at the time
            await ManagementBot.start_polling()

        await asyncio.get_running_loop().create_future()
    except (SystemExit, KeyboardInterrupt):
        print("Shutting Down")
        await server_context.shutdown()
        await ManagementBot.stop_polling()
        await ManagementBot.close_client_session()
        return


if __name__ == "__main__":
    asyncio.run(main())
