import traceback
from typing import Callable, Optional

import aiocoap.resource as resource  # type: ignore
from aiocoap import CHANGED, INTERNAL_SERVER_ERROR, Message  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession

from app.managers.aiq_manager import AiqDataManager
from app.telegram.bot import ManagementBot
from app.repositories.aiq_coap.managers import AiqDataCoapForwarder
from app.repositories.aiq_coap.client import CoapClient


class AiqDataResource(resource.Resource):
    def __init__(self, forward: bool, location_id: str, session_manager: Callable[[], AsyncSession], coap_client: Optional[CoapClient]):
        super().__init__()
        self.forward = forward
        self.location_id = location_id
        self.session_manager = session_manager
        self.coap_client = coap_client

    async def render_put(self, request) -> Message:
        try:
            message = request.payload.decode("ascii")
            if self.forward and self.coap_client:
                AiqDataCoapForwarder.forward_aiq_data(self.coap_client, message)
            session = self.session_manager()
            await AiqDataManager.save_sensor_data(session, message, self.location_id)
        except Exception:
            trace = traceback.format_exc()
            await ManagementBot.send_notification(f"An error occurred:\n {trace}")
            return Message(code=INTERNAL_SERVER_ERROR, payload="")
        return Message(code=CHANGED, payload="")
