import asyncio
import signal
import sys
from functools import partial

import aiocoap  # type: ignore
import aiocoap.resource as resource  # type: ignore

from app.config.env_manager import get_settings
from app.log import log
from app.managers.aiq_manager import AiqDataManager
from app.managers.br_manager import BorderRouterManager
from app.managers.station_manager import StationManager
from app.repositories.aiq_coap.client import CoapClient
from app.repositories.mysql.database import MysqlConnector
from app.repositories.postgres.database import PostgresqlConnector
from app.resources import StationDataStorageResource, IndexResource
from app.resources.station_data_forwarder import StationDataForwarderResource
from app.security.payload_validator import PayloadValidator
from app.telegram.bot import ManagementBot

EnvManager = get_settings()


def signal_exit() -> None:
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_exit)  # type: ignore
signal.signal(signal.SIGINT, signal_exit)  # type: ignore


async def main() -> None:
    # Init external resources
    log.info("Initializing DB resources")
    PostgresqlConnector.init_db(EnvManager.get_main_db_url())
    MysqlConnector.init_db(EnvManager.get_backup_db_url())
    ManagementBot.init_bot(EnvManager.BOT_TOKEN, EnvManager.get_allowed_users(), EnvManager.get_notification_user())
    PayloadValidator.init_validator(EnvManager.SECRET_KEY)

    log.info("Initializing COAP resources")
    binds = (EnvManager.BIND or "localhost", None) if EnvManager.is_dev() else None
    main_coap_context = await aiocoap.Context.create_server_context(None, bind=binds)

    server = resource.Site()
    aiq_data_resource = None

    if EnvManager.is_main_server():
        aiq_data_resource = StationDataStorageResource(
            PostgresqlConnector.get_session,
            MysqlConnector.get_session,
            PayloadValidator,
            EnvManager.SEVRER_INSTANCE_ID,
            EnvManager.allow_backups(),
        )

    else:
        assert EnvManager.MAIN_SERVER_URI, "Border Routers need MAIN_SERVER_URI to be valid"
        main_coap_client = CoapClient.get_instance(EnvManager.MAIN_SERVER_URI, main_coap_context)
        aiq_data_resource = StationDataForwarderResource(
            MysqlConnector.get_session,
            PayloadValidator,
            EnvManager.SEVRER_INSTANCE_ID,
            main_coap_client,
            EnvManager.allow_backups(),
        )

    server.add_resource(["aiq-data"], aiq_data_resource)
    server.add_resource(["index"], IndexResource(EnvManager.VERSION))

    # Register bot commands to manage border routers and main server
    if EnvManager.is_main_server():
        log.info("Initializing Telegram BOT Commands")
        ManagementBot.register_commad("data_summary", partial(AiqDataManager.get_summary, PostgresqlConnector.get_session))
        ManagementBot.register_commad("station_summary", partial(StationManager.get_station_summary, PostgresqlConnector.get_session))
        ManagementBot.register_commad(
            "register_station",
            partial(StationManager.register_sensor_station, PostgresqlConnector.get_session, MysqlConnector.get_session),
        )
        ManagementBot.register_commad(
            "br_summary", partial(BorderRouterManager.get_border_router_summary, PostgresqlConnector.get_session)
        )
        ManagementBot.register_commad(
            "register_br",
            partial(BorderRouterManager.register_border_router, PostgresqlConnector.get_session, MysqlConnector.get_session),
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
