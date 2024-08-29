from datetime import datetime, timezone
from typing import Optional


from app.types import AsyncSessionMaker
from sqlalchemy import delete, func, select

from app.repositories.db.models import ENS160Data, SCD41Data, StationData
from app.serializers.request import AiqDataFromStation

SUMMARY_TEMPLATE = """
Row Count: {}
SCD41:
\tco2: {} ppm
\ttemp: {} C
\thum: {} H%
ENS160:
\taqi: {}
\teco2: {} ppm
\ttvoc: {} ppb
border_router_id: {}
station_id: {}
"""


def _render_summary_template(data: StationData, count: int) -> str:
    return SUMMARY_TEMPLATE.format(
        count,
        int(data.scd41_data.co2) / 1000000,
        int(data.scd41_data.temperature) / 1000000,
        int(data.scd41_data.humidity) / 1000000,
        data.ens160_data.aqi,
        data.ens160_data.eco2,
        data.ens160_data.tvoc,
        data.border_router_id,
        data.station_id,
    )


class AiqDataManager:
    @staticmethod
    async def save_sensor_data(
        session_maker: AsyncSessionMaker,
        data: AiqDataFromStation,
        border_router_id: Optional[int] = None,
    ) -> int:
        sensor_data = StationData(
            station_id=data.station_id,
            timestamp=str(int(datetime.now(tz=timezone.utc).timestamp())),
            border_router_id=border_router_id,
        )

        if data.scd41:
            sensor_data.scd41_data = SCD41Data(
                co2=data.scd41.co2.to_str_number(),
                temperature=data.scd41.temp.to_str_number(),
                humidity=data.scd41.hum.to_str_number(),
            )

        if data.ens160:
            sensor_data.ens160_data = ENS160Data(eco2=data.ens160.eco2, tvoc=data.ens160.tvoc, aqi=data.ens160.aqi)

        async with session_maker() as session:
            session.add(sensor_data)
            await session.commit()

        return sensor_data.id

    @staticmethod
    async def get_sensor_data_by_id(session_maker: AsyncSessionMaker, id: int) -> Optional[StationData]:
        async with session_maker() as session:
            result = await session.execute(select(StationData).where(StationData.id == id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_summary(session_maker: AsyncSessionMaker) -> str:
        query = select(StationData).order_by(StationData.id.desc()).limit(1)
        async with session_maker() as session:
            result = (await session.scalars(query)).first()
            if not result:
                return "Database is empty"
            count = await session.scalar(select(func.count()).select_from(StationData))

        return _render_summary_template(result, count or 0)

    @staticmethod
    async def get_summary_by_station_id(session_maker: AsyncSessionMaker, station_id: int, border_router_id: int) -> str:
        query = (
            select(StationData)
            .where(StationData.station_id == station_id)
            .where(StationData.border_router_id == border_router_id)
            .order_by(StationData.id.desc())
            .limit(1)
        )

        async with session_maker() as session:
            result = (await session.scalars(query)).first()

            if not result:
                return f"Results for sensor {station_id} ans br_id {border_router_id}  not found"

        return _render_summary_template(result, 1)

    @staticmethod
    async def truncate_db(session_maker: AsyncSessionMaker) -> str:
        query = select(StationData.id).order_by(StationData.id.desc()).limit(120)
        async with session_maker() as session:
            ids = (await session.scalars(query)).all()
            if not ids:
                return "Database is empty"

            await session.execute(delete(StationData).where(StationData.id.in_(ids)))
            await session.commit()
        return "Truncate succesful"
