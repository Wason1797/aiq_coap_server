from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.db.models import BorderRouter


class AiqDataManager:
    @staticmethod
    async def register_border_router(session_maker: Callable[[], AsyncSession], ip_addr: str, location_id: str) -> None:
        async with session_maker() as session:
            query = select(BorderRouter).where(location_id == location_id).limit(1)
            current_br = (await session.scalars(query)).first()

            if current_br:
                current_br.ipv4_address = ip_addr
                await session.commit()
                return

            session.add(
                BorderRouter(
                    ipv4_address=ip_addr,
                    location_id=location_id,
                )
            )
            await session.commit()
