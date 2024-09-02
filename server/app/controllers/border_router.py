from app.types import AsyncSessionMaker

from app.managers.br_manager import BorderRouterManager
from app.repositories.aiq_coap.client import CoapClient, Context
from app.repositories.aiq_coap.managers import AiqBorderRouterCoapClient


class BorderRouterController:
    @staticmethod
    async def query_br_summary(session_maker: AsyncSessionMaker, context: Context, border_router_id: int) -> str:
        br = await BorderRouterManager.get_border_router_by_id(session_maker, border_router_id)

        if not br:
            return f"BR for id {border_router_id} not found"

        coap_client = CoapClient(f"coap://{br.ipv4_address}/aiq-management/summary", context)
        return await AiqBorderRouterCoapClient.get_summary(coap_client)

    @staticmethod
    async def truncate_br_database(session_maker: AsyncSessionMaker, context: Context, border_router_id: int) -> str:
        br = await BorderRouterManager.get_border_router_by_id(session_maker, border_router_id)

        if not br:
            return f"BR for id {border_router_id} not found"

        coap_client = CoapClient(f"coap://{br.ipv4_address}/aiq-management/truncate", context)
        return await AiqBorderRouterCoapClient.truncate_database(coap_client)
