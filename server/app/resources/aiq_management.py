import traceback


import aiocoap.resource as resource  # type: ignore
from aiocoap import CONTENT, INTERNAL_SERVER_ERROR, Message
from app.managers.aiq_manager import AiqDataManager  # type: ignore
from app.types import AsyncSessionMaker

from app.telegram.bot import ManagementBot


class AiqManagementSummaryResource(resource.Resource):
    def __init__(
        self,
        border_router_id: int,
        main_session: AsyncSessionMaker,
    ):
        super().__init__()
        self.border_router_id = border_router_id
        self.main_session = main_session

    async def render_get(self, request) -> Message:
        try:
            summary = await AiqDataManager.get_summary(self.main_session)

        except Exception:
            trace = traceback.format_exc()
            await ManagementBot.send_notification(f"An error occurred in border router{self.border_router_id}:\n {trace}")
            return Message(code=INTERNAL_SERVER_ERROR, payload="")

        return Message(code=CONTENT, payload=summary.encode("ascii"))


class AiqManagementTruncateResource(resource.Resource):
    def __init__(
        self,
        border_router_id: int,
        main_session: AsyncSessionMaker,
    ):
        super().__init__()
        self.border_router_id = border_router_id
        self.main_session = main_session

    async def render_delete(self, request) -> Message:
        try:
            truncate_result = await AiqDataManager.truncate_db(self.main_session)

        except Exception:
            trace = traceback.format_exc()
            await ManagementBot.send_notification(f"An error occurred in {self.border_router_id}:\n {trace}")
            return Message(code=INTERNAL_SERVER_ERROR, payload="")

        return Message(code=CONTENT, payload=truncate_result.encode("ascii"))
