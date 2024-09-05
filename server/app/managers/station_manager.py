from typing import Optional
from app.types import AsyncSessionMaker, AsyncSession
from sqlalchemy import select

from app.repositories.db.models import Station


class StationManager:
    @staticmethod
    async def register_sensor_station(
        session_maker: AsyncSessionMaker, backup_session: AsyncSessionMaker, name: str, station_id: Optional[int]
    ) -> str:
        async def _upsert_sensor_station(session: AsyncSession):
            if station_id:
                query = select(Station).where(Station.id == station_id).limit(1)
                current_station = (await session.scalars(query)).first()

                if current_station:
                    current_station.name = name
                    await session.commit()
                    return f"Updated Sensor station {current_station.id} {current_station.name}"
                else:
                    return f"Sensor station with id {station_id} not found"
            else:
                new_station = Station(
                    name=name,
                )
                session.add(new_station)
                await session.commit()

                return f"Sensor station registered with id: {new_station.id} | {new_station.name}"

        async with session_maker() as session:
            result_main = _upsert_sensor_station(session)

        async with backup_session() as backup_session:
            result_backup = _upsert_sensor_station(backup_session)

        return f"{result_main}\n{result_backup}"

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
