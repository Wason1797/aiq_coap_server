import asyncio
from typing import Type, cast

import aiocoap.resource as resource  # type: ignore
from aiocoap import CHANGED, INTERNAL_SERVER_ERROR, Message  # type: ignore

from app.log import log
from app.managers.aiq_manager import AiqDataManager
from app.repositories.aiq_coap.client import CoapClient
from app.repositories.aiq_coap.managers import AiqDataCoapForwarder
from app.security.payload_validator import PayloadValidator
from app.serializers.request import AiqDataFromStation
from app.types import AsyncSessionMaker


class StationDataForwarderResource(resource.Resource):
    def __init__(
        self,
        backup_session: AsyncSessionMaker,
        payload_validator: Type[PayloadValidator],
        server_instance_id: int,
        coap_client: CoapClient,
        allow_backups: bool = False,
    ):
        super().__init__()
        self.backup_session = backup_session
        self.payload_validator = payload_validator
        self.coap_client = coap_client
        self.server_instance_id = server_instance_id
        self.allow_backups = allow_backups

    async def render_put(self, request) -> Message:
        try:
            payload: str = request.payload.decode("ascii")
            log.info(f"[COAP] forwarder request {payload}")

            validated_payload = self.payload_validator.validate(payload, AiqDataFromStation)

            sensor_data = cast(AiqDataFromStation, validated_payload.data)
            border_router_id = validated_payload.border_router_id or self.server_instance_id

            AiqDataCoapForwarder.forward_aiq_data(self.coap_client, payload, border_router_id)

            if self.allow_backups:
                await AiqDataManager.save_sensor_data(self.backup_session, sensor_data, border_router_id)
            else:
                await asyncio.sleep(0.01)  # Await something so the background task has time to schedule/run.

        except Exception:
            log.exception("Error in StationDataForwarderResource", exc_info=True)
            return Message(code=INTERNAL_SERVER_ERROR, payload="Error forwarding data")

        return Message(code=CHANGED, payload="")
