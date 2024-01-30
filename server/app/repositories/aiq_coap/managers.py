import traceback
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
