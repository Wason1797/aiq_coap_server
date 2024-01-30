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
    def __init__(
        self,
        is_main_server: bool,
        location_id: str,
        main_session: Callable[[], AsyncSession],
        backup_session: Callable[[], AsyncSession],
        coap_client: Optional[CoapClient],
    ):
        super().__init__()
        self.is_main_server = is_main_server
        self.location_id = location_id
        self.main_session = main_session
        self.backup_session = backup_session
        self.coap_client = coap_client

    async def render_put(self, request) -> Message:
        try:
            try:
                message = request.payload.decode("ascii")
            except Exception as ex:
                ex.add_note("Error in payload decoding or serialization")
                raise ex

            if not self.is_main_server and self.coap_client:
                AiqDataCoapForwarder.forward_aiq_data(self.coap_client, message)

            should_backup = False

            try:
                session = self.main_session()
                await AiqDataManager.save_sensor_data(session, message, self.location_id)
            except Exception as ex:
                should_backup = True
                ex.add_note("Error when storing in the main database")
                raise ex

            if self.is_main_server or should_backup:
                try:
                    backup_session = self.backup_session()
                    await AiqDataManager.save_sensor_data(backup_session, message, self.location_id)
                except Exception as ex:
                    ex.add_note("Error when storing in the backup database")
                    raise ex

        except Exception:
            trace = traceback.format_exc()
            await ManagementBot.send_notification(f"An error occurred in {self.location_id}:\n {trace}")
            return Message(code=INTERNAL_SERVER_ERROR, payload="")

        return Message(code=CHANGED, payload="")
