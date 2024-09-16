from typing import Optional
from app.types import AsyncSessionMaker, AsyncSession
from sqlalchemy import select

from app.repositories.db.models import Station


class StationManager:
    @staticmethod
    async def register_sensor_station(
        main_session: AsyncSessionMaker, backup_session: AsyncSessionMaker, name: str, station_id: Optional[int]
    ) -> str:
        async def _upsert_border_router(session: AsyncSession, station: Station | None, id_from_db: int | None = None) -> Station:
            if station:
                station.name = name
                await session.commit()
                return station

            new_station = Station(
                name=name,
            )
            if id_from_db:
                new_station.id = id_from_db

            session.add(new_station)
            await session.commit()

            return new_station

        query = select(Station).where(Station.id == station_id).limit(1)
        async with main_session() as session:
            station_from_main_db = (await session.scalars(query)).first() if station_id else None

            if station_from_main_db is None and station_id:
                return f"Sensor Station router with {station_id} not found"

            main_station = await _upsert_border_router(session, station_from_main_db)

        async with backup_session() as session:
            station_from_backup_db = (await session.scalars(query)).first() if station_id else None
            id_to_send = main_station.id if station_from_backup_db is None else None
            await _upsert_border_router(session, station_from_backup_db, id_to_send)

        return f"Station router registered with id: {main_station.id} | {main_station.name}"

    @staticmethod
    async def get_station_by_id(session_maker: AsyncSessionMaker, id: int) -> Station | None:
        async with session_maker() as session:
            query = select(Station).where(Station.id == id).limit(1)
            return (await session.scalars(query)).first()

    @staticmethod
    async def get_station_summary(session_maker: AsyncSessionMaker) -> str:
        async with session_maker() as session:
            stations = (await session.scalars(select(Station))).all()

        if not stations:
            return "No sensor stations were found"
        summary = "\n".join(f"{st.id}\t{st.name}" for st in stations)
        return f"id\tname\n{summary}"
