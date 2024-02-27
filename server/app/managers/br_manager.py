from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.db.models import BorderRouter


class BorderRouterManager:
    @staticmethod
    async def register_border_router(session_maker: Callable[[], AsyncSession], location_id: str, ip_addr: str) -> str:
        async with session_maker() as session:
            query = select(BorderRouter).where(BorderRouter.location_id == location_id).limit(1)
            current_br = (await session.scalars(query)).first()

            if current_br:
                current_br.ipv4_address = ip_addr
                await session.commit()
                return f"Updated Border router {location_id} {ip_addr}"

            session.add(
                BorderRouter(
                    ipv4_address=ip_addr,
                    location_id=location_id,
                )
            )
            await session.commit()

        return f"Border router registered {location_id} {ip_addr}"

    @staticmethod
    async def get_border_router(session_maker: Callable[[], AsyncSession], location_id: str) -> BorderRouter | None:
        async with session_maker() as session:
            query = select(BorderRouter).where(BorderRouter.location_id == location_id).limit(1)
            return (await session.scalars(query)).first()
