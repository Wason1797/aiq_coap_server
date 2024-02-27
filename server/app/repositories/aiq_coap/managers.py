import traceback
from typing import Optional
from app.serializers.request import AiqDataFromStation
from app.telegram.bot import ManagementBot
from .client import CoapClient

import asyncio


class AiqDataCoapForwarder:
    @staticmethod
    def forward_aiq_data(coap_client: CoapClient, data: str) -> asyncio.Task:
        async def forward_data_task() -> None:
            try:
                AiqDataFromStation.model_validate_json(data)
                response = await coap_client.put_payload(data)
                print(f"Forwarded {response.code}, {response.payload}")
            except Exception:
                trace = traceback.format_exc()
                await ManagementBot.send_notification(f"An error occurred while forwarding to {coap_client.server_uri}:\n {trace}")

        task = asyncio.create_task(forward_data_task())  # Schedule the task in the background
        return task


class AiqBorderRouterCoapClient:
    @staticmethod
    async def get_summary(coap_client: CoapClient, sensor_id: int) -> Optional[str]:
        try:
            response = await coap_client.get_payload(str(sensor_id))
            return response.payload
        except Exception:
            trace = traceback.format_exc()
            await ManagementBot.send_notification(
                f"An error occurred while getting summary for sensor {sensor_id}, BR: {coap_client.server_uri}:\n {trace}"
            )
            return None

    @staticmethod
    async def truncate_database(coap_client: CoapClient) -> Optional[str]:
        try:
            response = await coap_client.delete_payload("")
            return response.payload
        except Exception:
            trace = traceback.format_exc()
            await ManagementBot.send_notification(f"An error occurred while truncating database for BR {coap_client.server_uri}:\n {trace}")
            return None
