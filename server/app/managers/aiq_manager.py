from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import delete, func, select

from app.repositories.db.models import ENS160Data, SCD41Data, StationData, SVM41Data
from app.serializers.request import AiqDataFromStation
from app.types import AsyncSessionMaker

SUMMARY_TEMPLATE = """
Row Count: {}
{}
{}
border_router_id: {}
station_id: {}
"""

SCD41_SUMMARY_TEMPLATE = """
SCD41:
\tco2: {} ppm
\ttemp: {} C
\thum: {} H%
"""

ENS160_SUMMARY_TEMPLATE = """
ENS160:
\taqi: {}
\teco2: {} ppm
\ttvoc: {} ppb
"""


def _render_summary_template(data: StationData, count: int) -> str:
    scd41_summary = (
        SCD41_SUMMARY_TEMPLATE.format(
            int(data.scd41_data.co2) / 1000000,
            int(data.scd41_data.temperature) / 1000000,
            int(data.scd41_data.humidity) / 1000000,
        )
        if data.scd41_data is not None
        else ""
    )

    ens160_summary = (
        ENS160_SUMMARY_TEMPLATE.format(
            data.ens160_data.aqi,
            data.ens160_data.eco2,
            data.ens160_data.tvoc,
        )
        if data.ens160_data is not None
        else ""
    )

    return SUMMARY_TEMPLATE.format(
        count,
        scd41_summary,
        ens160_summary,
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

        if data.scd41_d:
            sensor_data.scd41_data = SCD41Data(
                co2=data.scd41_d.co2.to_str_number(),
                temperature=data.scd41_d.temp.to_str_number(),
                humidity=data.scd41_d.hum.to_str_number(),
            )

        if data.ens160_d:
            sensor_data.ens160_data = ENS160Data(eco2=data.ens160_d.eco2, tvoc=data.ens160_d.tvoc, aqi=data.ens160_d.aqi)

        if data.svm41_d:
            sensor_data.svm41_data = SVM41Data(
                temperature=data.svm41_d.temp.to_str_number(),
                humidity=data.svm41_d.hum.to_str_number(),
                nox_index=data.svm41_d.nox.to_str_number(),
                voc_index=data.svm41_d.voc.to_str_number(),
            )

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
    async def get_summary_by_station_id(session_maker: AsyncSessionMaker, station_id: int) -> str:
        query = select(StationData).where(StationData.station_id == station_id).order_by(StationData.id.desc()).limit(1)

        async with session_maker() as session:
            result = (await session.scalars(query)).first()

            if not result:
                return f"Results for sensor {station_id}  not found"

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
