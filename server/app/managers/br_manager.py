from sqlalchemy import select

from app.repositories.db.models import BorderRouter
from app.types import AsyncSession, AsyncSessionMaker


class BorderRouterManager:
    @staticmethod
    async def register_border_router(
        main_session: AsyncSessionMaker,
        backup_session: AsyncSessionMaker,
        ip_addr: str,
        location: str,
        border_router_id: int | None = None,
    ) -> str:
        async def _upsert_border_router(session: AsyncSession, br: BorderRouter | None, id_from_db: int | None = None) -> BorderRouter:
            if br:
                br.ipv4_address = ip_addr
                br.location = location
                await session.commit()
                return br

            new_br = BorderRouter(
                ipv4_address=ip_addr,
                location=location,
            )
            if id_from_db:
                new_br.id = id_from_db

            session.add(new_br)
            await session.commit()

            return new_br

        query = select(BorderRouter).where(BorderRouter.id == border_router_id).limit(1)
        async with main_session() as session:
            br_from_main_db = (await session.scalars(query)).first() if border_router_id else None

            if br_from_main_db is None and border_router_id:
                return f"Border router with {border_router_id} not found"

            main_br = await _upsert_border_router(session, br_from_main_db)

        async with backup_session() as session:
            br_from_backup_db = (await session.scalars(query)).first() if border_router_id else None
            id_to_send = main_br.id if br_from_backup_db is None else None
            await _upsert_border_router(session, br_from_backup_db, id_to_send)

        return f"Border router registered with id: {main_br.id} | {main_br.location} | {main_br.ipv4_address}"

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
            border_routers = (await session.scalars(select(BorderRouter).order_by(BorderRouter.id))).all()

        if not border_routers:
            return "No border routers were found"
        summary = "\n".join(f"{br.id}\t{br.ipv4_address}\t{br.location}" for br in border_routers)
        return f"id\tip\tlocation\n{summary}"
