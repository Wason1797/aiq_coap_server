import aiocoap.resource as resource
from aiocoap import CHANGED, INTERNAL_SERVER_ERROR, Message

from app.config.env_manager import get_settings
from app.repositories.postgres.database import PostgresqlConnector
from app.repositories.postgres.managers import AiqDataManager

from app.telegram.bot import ManagementBot

import traceback

EnvManager = get_settings()


class AiqDataResource(resource.Resource):
    def __init__(self):
        super().__init__()

    async def render_put(self, request) -> Message:
        try:
            message = request.payload.decode("ascii")
            session = PostgresqlConnector.get_session()
            await AiqDataManager.save_sensor_data(session, message, EnvManager.LOCATION_ID)
        except Exception:
            trace = traceback.format_exc()
            await ManagementBot.bot().send_message(EnvManager.get_notification_user(), f"An error occurred:\n {trace}")
            return Message(code=INTERNAL_SERVER_ERROR, payload="")
        return Message(code=CHANGED, payload="")
