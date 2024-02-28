from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.managers.br_manager import BorderRouterManager
from app.repositories.aiq_coap.client import CoapClient, Context
from app.repositories.aiq_coap.managers import AiqBorderRouterCoapClient


class BorderRouterController:
    @staticmethod
    async def query_br_summary(session_maker: Callable[[], AsyncSession], context: Context, location_id: str, sensor_id: int) -> str:
        br = await BorderRouterManager.get_border_router(session_maker, location_id)

        if not br:
            return f"BR for {location_id} not found"

        coap_client = CoapClient(f"coap://{br.ipv4_address}/aiq-management/summary", context)
        return await AiqBorderRouterCoapClient.get_summary(coap_client, sensor_id)

    @staticmethod
    async def truncate_br_database(session_maker: Callable[[], AsyncSession], context: Context, location_id: str) -> str:
        br = await BorderRouterManager.get_border_router(session_maker, location_id)

        if not br:
            return f"BR for {location_id} not found"

        coap_client = CoapClient(f"coap://{br.ipv4_address}/aiq-management/truncate", context)
        return await AiqBorderRouterCoapClient.truncate_database(coap_client)
