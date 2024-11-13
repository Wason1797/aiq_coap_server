import asyncio
import traceback

from app.log import log

from .client import CoapClient


class AiqDataCoapForwarder:
    background_tasks: set = set()

    @classmethod
    def forward_aiq_data(cls, coap_client: CoapClient, data: str, border_router_id: int) -> asyncio.Task:
        async def forward_data_task() -> None:
            try:
                log.info("Forwarding")
                response = await coap_client.put_payload(f"{data}|{border_router_id}")
                await asyncio.sleep(0.01)
                log.info(f"Forwarded {response.code}, {response.payload}")
            except Exception as ex:
                log.exception("Error while forwarding payload")
                raise ex

        task = asyncio.create_task(forward_data_task())  # Schedule the task in the background
        cls.background_tasks.add(task)
        task.add_done_callback(cls.background_tasks.discard)
        return task


class AiqBorderRouterCoapClient:
    @staticmethod
    async def get_summary(coap_client: CoapClient) -> str:
        try:
            response = await coap_client.get_payload("")
            return response.payload
        except Exception:
            trace = traceback.format_exc()
            return f"An error occurred while getting summary for BR: {coap_client.server_uri}:\n {trace}"

    @staticmethod
    async def truncate_database(coap_client: CoapClient) -> str:
        try:
            response = await coap_client.delete_payload("")
            return response.payload
        except Exception:
            trace = traceback.format_exc()
            return f"An error occurred while truncating database for BR {coap_client.server_uri}:\n {trace}"
