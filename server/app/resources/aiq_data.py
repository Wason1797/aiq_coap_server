import traceback
from typing import Callable

import aiocoap.resource as resource  # type: ignore
from aiocoap import CHANGED, INTERNAL_SERVER_ERROR, Message  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.postgres.managers import AiqDataManager
from app.telegram.bot import ManagementBot


class AiqDataResource(resource.Resource):
    def __init__(self, location_id: str, session_manager: Callable[[], AsyncSession]):
        super().__init__()
        self.location_id = location_id
        self.session_manager = session_manager

    async def render_put(self, request) -> Message:
        try:
            message = request.payload.decode("ascii")
            session = self.session_manager()
            await AiqDataManager.save_sensor_data(session, message, self.location_id)
        except Exception:
            trace = traceback.format_exc()
            await ManagementBot.send_notification(f"An error occurred:\n {trace}")
            return Message(code=INTERNAL_SERVER_ERROR, payload="")
        return Message(code=CHANGED, payload="")
