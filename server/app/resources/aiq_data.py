import traceback
from typing import Callable, Optional, Type, cast

import aiocoap.resource as resource  # type: ignore
from aiocoap import CHANGED, INTERNAL_SERVER_ERROR, Message  # type: ignore
from app.security.payload_validator import PayloadValidator
from app.serializers.request import AiqDataFromStation
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
        payload_validator: Type[PayloadValidator],
    ):
        super().__init__()
        self.is_main_server = is_main_server
        self.location_id = location_id
        self.main_session = main_session
        self.backup_session = backup_session
        self.coap_client = coap_client
        self.payload_validator = payload_validator

    async def render_put(self, request) -> Message:
        try:
            payload: str = request.payload.decode("ascii")
            print("[COAP] got request", payload)

            sensor_data = cast(AiqDataFromStation, self.payload_validator.validate(payload, AiqDataFromStation))

            if not self.is_main_server and self.coap_client:
                AiqDataCoapForwarder.forward_aiq_data(self.coap_client, payload)

            try:
                await AiqDataManager.save_sensor_data(self.main_session, sensor_data, self.location_id)
            except Exception as ex:
                ex.add_note("Could not store sensor data in main DB")
                await AiqDataManager.save_sensor_data(self.backup_session, sensor_data, self.location_id)
                raise ex

            if self.is_main_server:
                await AiqDataManager.save_sensor_data(self.backup_session, sensor_data, self.location_id)

        except Exception:
            trace = traceback.format_exc()
            await ManagementBot.send_notification(f"An error occurred in {self.location_id}:\n {trace}")
            return Message(code=INTERNAL_SERVER_ERROR, payload="")

        return Message(code=CHANGED, payload="")
