import asyncio
import signal
import sys
import logging
from functools import partial

import aiocoap  # type: ignore
import aiocoap.resource as resource  # type: ignore

from app.config.env_manager import get_settings
from app.managers.aiq_manager import AiqDataManager
from app.managers.br_manager import BorderRouterManager
from app.repositories.aiq_coap.client import CoapClient
from app.repositories.postgres.database import PostgresqlConnector
from app.repositories.mysql.database import MysqlConnector
from app.resources import AiqDataResource, AiqManagementTruncateResource, AiqManagementSummaryResource
from app.security.payload_validator import PayloadValidator
from app.telegram.bot import ManagementBot
from app.controllers.border_router import BorderRouterController

log = logging.getLogger(__name__)

EnvManager = get_settings()

signal.signal(signal.SIGTERM, lambda: sys.exit(0))
signal.signal(signal.SIGINT, lambda: sys.exit(0))


async def main() -> None:
    # Init external resources
    PostgresqlConnector.init_db(EnvManager.get_main_db_url())
    MysqlConnector.init_db(EnvManager.get_backup_db_url())
    ManagementBot.init_bot(EnvManager.BOT_TOKEN, EnvManager.get_allowed_users(), EnvManager.get_notification_user())
    PayloadValidator.init_validator(EnvManager.SECRET_KEY)

    binds = ("localhost", None) if EnvManager.is_dev() else None
    main_coap_context = await aiocoap.Context.create_server_context(None, bind=binds)
    main_coap_client = CoapClient.get_instance(EnvManager.MAIN_SERVER_URI, main_coap_context)

    server = resource.Site()
    server.add_resource(
        ["aiq-data"],
        AiqDataResource(
            EnvManager.is_main_server(),
            EnvManager.LOCATION_ID,
            PostgresqlConnector.get_session,
            MysqlConnector.get_session,
            main_coap_client,
            PayloadValidator,
        ),
    )

    if not EnvManager.is_main_server():  # Enable management interface for border routers
        server.add_resource(["aiq-management", "summary"], AiqManagementSummaryResource(EnvManager.LOCATION_ID, PostgresqlConnector.get_session))
        server.add_resource(["aiq-management", "truncate"], AiqManagementTruncateResource(EnvManager.LOCATION_ID, PostgresqlConnector.get_session))

    # Register bot commands to manage border routers and main server
    ManagementBot.register_commad("summary", partial(AiqDataManager.get_summary, PostgresqlConnector.get_session))
    ManagementBot.register_commad("register_br", partial(BorderRouterManager.register_border_router, PostgresqlConnector.get_session))
    ManagementBot.register_commad(
        "summary_station", partial(BorderRouterController.query_br_summary, PostgresqlConnector.get_session, main_coap_context)
    )
    ManagementBot.register_commad(
        "truncate", partial(BorderRouterController.truncate_br_database, PostgresqlConnector.get_session, main_coap_context)
    )

    log.info("Starting AIQ Server")
    asyncio.get_running_loop().add_signal_handler(signal.SIGINT, lambda: sys.exit(0))
    try:
        main_coap_context.serversite = server
        if EnvManager.is_main_server():  # Only one instance of the bot can run at the time
            await ManagementBot.start_polling()

        await asyncio.get_running_loop().create_future()
    except SystemExit:
        log.info("Shutting Down")
        await main_coap_context.shutdown()
        await ManagementBot.stop_polling()
        await ManagementBot.close_client_session()
        return
    finally:
        log.info("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
