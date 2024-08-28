from typing import Optional
from app.types import AsyncSessionMaker
from sqlalchemy import select

from app.repositories.db.models import BorderRouter


class BorderRouterManager:
    @staticmethod
    async def register_border_router(
        session_maker: AsyncSessionMaker, ip_addr: str, location: str, border_router_id: Optional[int]
    ) -> str:
        async with session_maker() as session:
            if border_router_id:
                query = select(BorderRouter).where(BorderRouter.id == border_router_id).limit(1)
                current_br = (await session.scalars(query)).first()

                if current_br:
                    current_br.ipv4_address = ip_addr
                    current_br.location = location
                    await session.commit()
                    return f"Updated Border router {border_router_id} {location} {ip_addr}"
                else:
                    return f"Border router with id {border_router_id} not found"
            else:
                session.add(
                    BorderRouter(
                        ipv4_address=ip_addr,
                        location=location,
                    )
                )
                await session.commit()

                return f"Border router registered {location} {ip_addr}"

    @staticmethod
    async def get_border_router(session_maker: AsyncSessionMaker, location: str) -> BorderRouter | None:
        async with session_maker() as session:
            query = select(BorderRouter).where(BorderRouter.location == location).limit(1)
            return (await session.scalars(query)).first()
