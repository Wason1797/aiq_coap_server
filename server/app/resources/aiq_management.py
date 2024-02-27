import traceback
from typing import Callable

import aiocoap.resource as resource  # type: ignore
from aiocoap import CONTENT, INTERNAL_SERVER_ERROR, Message
from app.managers.aiq_manager import AiqDataManager  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession

from app.telegram.bot import ManagementBot


class AiqManagementSummaryResource(resource.Resource):
    def __init__(
        self,
        is_main_server: bool,
        location_id: str,
        main_session: Callable[[], AsyncSession],
    ):
        super().__init__()
        self.is_main_server = is_main_server
        self.location_id = location_id
        self.main_session = main_session

    async def render_get(self, request) -> Message:
        try:
            sensor_id = int(request.payload.decode("ascii"))
            summary = await AiqDataManager.get_summary_by_sensor_and_location(self.main_session, sensor_id, self.location_id)

        except Exception:
            trace = traceback.format_exc()
            await ManagementBot.send_notification(f"An error occurred in {self.location_id}:\n {trace}")
            return Message(code=INTERNAL_SERVER_ERROR, payload="")

        return Message(code=CONTENT, payload=summary)


class AiqManagementTruncateResource(resource.Resource):
    def __init__(
        self,
        is_main_server: bool,
        location_id: str,
        main_session: Callable[[], AsyncSession],
    ):
        super().__init__()
        self.is_main_server = is_main_server
        self.location_id = location_id
        self.main_session = main_session

    async def render_delete(self, request) -> Message:
        try:
            truncate_result = await AiqDataManager.truncate_db(self.main_session)

        except Exception:
            trace = traceback.format_exc()
            await ManagementBot.send_notification(f"An error occurred in {self.location_id}:\n {trace}")
            return Message(code=INTERNAL_SERVER_ERROR, payload="")

        return Message(code=CONTENT, payload=truncate_result)
