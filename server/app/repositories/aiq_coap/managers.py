import asyncio
import traceback


from app.telegram.bot import ManagementBot

from .client import CoapClient


class AiqDataCoapForwarder:
    background_tasks: set = set()

    @classmethod
    def forward_aiq_data(cls, coap_client: CoapClient, data: str) -> None:
        async def forward_data_task() -> None:
            try:
                print("Forwarding")
                response = await coap_client.put_payload(data)
                await asyncio.sleep(0.01)
                print(f"Forwarded {response.code}, {response.payload}")
            except Exception:
                trace = traceback.format_exc()
                await ManagementBot.send_notification(f"An error occurred while forwarding to {coap_client.server_uri}:\n {trace}")

        task = asyncio.create_task(forward_data_task())  # Schedule the task in the background
        cls.background_tasks.add(task)
        task.add_done_callback(cls.background_tasks.discard)
        return None


class AiqBorderRouterCoapClient:
    @staticmethod
    async def get_summary(coap_client: CoapClient, sensor_id: int) -> str:
        try:
            response = await coap_client.get_payload(str(sensor_id))
            return response.payload
        except Exception:
            trace = traceback.format_exc()
            return f"An error occurred while getting summary for sensor {sensor_id}, BR: {coap_client.server_uri}:\n {trace}"

    @staticmethod
    async def truncate_database(coap_client: CoapClient) -> str:
        try:
            response = await coap_client.delete_payload("")
            return response.payload
        except Exception:
            trace = traceback.format_exc()
            return f"An error occurred while truncating database for BR {coap_client.server_uri}:\n {trace}"
