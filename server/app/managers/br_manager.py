from typing import Optional
from app.types import AsyncSessionMaker, AsyncSession
from sqlalchemy import select

from app.repositories.db.models import BorderRouter


class BorderRouterManager:
    @staticmethod
    async def register_border_router(
        session_maker: AsyncSessionMaker,
        backup_session: AsyncSessionMaker,
        ip_addr: str,
        location: str,
        border_router_id: Optional[int],
    ) -> str:
        async def _upsert_border_router(session: AsyncSession):
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
                new_br = BorderRouter(
                    ipv4_address=ip_addr,
                    location=location,
                )
                session.add(new_br)
                await session.commit()

                return f"Border router registered with id: {new_br.id} | {location} | {ip_addr}"

        async with session_maker() as session:
            main_result = _upsert_border_router(session)

        async with backup_session() as backup_session:
            backup_result = _upsert_border_router(backup_session)

        return f"{main_result}\n{backup_result}"

    @staticmethod
    async def get_border_router(session_maker: AsyncSessionMaker, location: str) -> BorderRouter | None:
        async with session_maker() as session:
            query = select(BorderRouter).where(BorderRouter.location == location).limit(1)
            return (await session.scalars(query)).first()

    @staticmethod
    async def get_border_router_by_id(session_maker: AsyncSessionMaker, id: int) -> BorderRouter | None:
        async with session_maker() as session:
            query = select(BorderRouter).where(BorderRouter.id == id).limit(1)
            return (await session.scalars(query)).first()

    @staticmethod
    async def get_border_router_summary(session_maker: AsyncSessionMaker) -> str:
        async with session_maker() as session:
            border_routers = (await session.scalars(select(BorderRouter))).all()

        if not border_routers:
            return "No border routers were found"
        summary = "\n".join(f"{br.id}\t{br.ipv4_address}\t{br.location}" for br in border_routers)
        return f"id\tip\tlocation\n{summary}"
