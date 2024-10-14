import traceback
from typing import Optional, Type, cast

import aiocoap.resource as resource  # type: ignore
from aiocoap import CHANGED, INTERNAL_SERVER_ERROR, Message  # type: ignore

from app.log import log
from app.managers.aiq_manager import AiqDataManager
from app.security.payload_validator import PayloadValidator
from app.serializers.request import AiqDataFromStation
from app.telegram.bot import ManagementBot
from app.types import AsyncSessionMaker


class AiqDataResource(resource.Resource):
    def __init__(
        self,
        main_session: AsyncSessionMaker,
        backup_session: AsyncSessionMaker,
        payload_validator: Type[PayloadValidator],
        server_instance_id: Optional[int] = None,
        allow_backups: bool = False,
    ):
        super().__init__()
        self.main_session = main_session
        self.backup_session = backup_session
        self.server_instance_id = server_instance_id
        self.payload_validator = payload_validator
        self.allow_backups = allow_backups

    async def render_put(self, request) -> Message:
        try:
            payload: str = request.payload.decode("ascii")
            log.info(f"[COAP] got request {payload}")

            validated_payload = self.payload_validator.validate(payload, AiqDataFromStation)

            sensor_data = cast(AiqDataFromStation, validated_payload.data)
            border_router_id = validated_payload.border_router_id or self.server_instance_id

            # if not self.is_main_server and self.coap_client:
            #     AiqDataCoapForwarder.forward_aiq_data(self.coap_client, payload, self.border_router_id or 0)

            try:
                await AiqDataManager.save_sensor_data(self.main_session, sensor_data, border_router_id)
            except Exception as ex:
                if self.allow_backups:
                    await AiqDataManager.save_sensor_data(self.backup_session, sensor_data, border_router_id)

                ex.add_note("Could not store sensor data in main DB")
                raise ex

            if self.allow_backups:
                await AiqDataManager.save_sensor_data(self.backup_session, sensor_data, border_router_id)

        except Exception:
            trace = traceback.format_exc()
            await ManagementBot.send_notification(f"An error occurred in server with id {self.server_instance_id}:\n {trace}")
            return Message(code=INTERNAL_SERVER_ERROR, payload="")

        return Message(code=CHANGED, payload="")
