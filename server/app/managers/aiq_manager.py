from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import delete, func, select

from app.repositories.db.models import BME688Data, ENS160Data, SCD41Data, SFA30Data, StationData, SVM41Data
from app.serializers.request import AiqDataFromStation
from app.types import AsyncSessionMaker

SUMMARY_TEMPLATE = """
Row Count: {}
Last Date: {}
{}
{}
{}
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

SVM41_SUMMARY_TEMPLATE = """
SVM41:
\ttemp: {} C
\thum: {} H%
\tnox: {} 
\tvoc: {} 
"""

BME688_SUMMARY_TEMPLATE = """
BME688:
\ttemp: {} C
\thum: {} H%
\tpress: {} KPa
\tgasres: {} Ohm
"""

SFA30_SUMMARY_TEMPLATE = """
SFA30:
\thco: {} ppb
\ttemp: {} C
\thum: {} H%
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

    svm41_summary = (
        SVM41_SUMMARY_TEMPLATE.format(
            int(data.svm41_data.temperature) / 1000000,
            int(data.svm41_data.humidity) / 1000000,
            int(data.svm41_data.nox_index) / 1000000,
            int(data.svm41_data.voc_index) / 1000000,
        )
        if data.svm41_data is not None
        else ""
    )

    bme688_summary = (
        BME688_SUMMARY_TEMPLATE.format(
            int(data.bme688_data.temperature) / 1000000,
            int(data.bme688_data.humidity) / 1000000,
            int(data.bme688_data.pressure) / 1000000,
            int(data.bme688_data.gas_resistance) / 1000000,
        )
        if data.bme688_data is not None
        else ""
    )

    sfa30_summary = (
        SFA30_SUMMARY_TEMPLATE.format(
            int(data.sfa30_data.hco) / 1000000,
            int(data.sfa30_data.temperature) / 1000000,
            int(data.sfa30_data.humidity) / 1000000,
        )
        if data.sfa30_data is not None
        else ""
    )

    return SUMMARY_TEMPLATE.format(
        count,
        datetime.fromtimestamp(float(data.timestamp), timezone.utc).strftime(r"%d/%m/%Y, %H:%M:%S"),
        scd41_summary,
        ens160_summary,
        svm41_summary,
        bme688_summary,
        sfa30_summary,
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

        if data.bme688_d:
            sensor_data.bme688_data = BME688Data(
                temperature=data.bme688_d.temp.to_str_number(),
                humidity=data.bme688_d.hum.to_str_number(),
                pressure=data.bme688_d.press.to_str_number(),
                gas_resistance=data.bme688_d.gasres.to_str_number(),
            )

        if data.sfa30_d:
            sensor_data.sfa30_data = SFA30Data(
                hco=data.sfa30_d.hco.to_str_number(),
                temperature=data.sfa30_d.temp.to_str_number(),
                humidity=data.sfa30_d.hum.to_str_number(),
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
    async def get_summary(session_maker: AsyncSessionMaker, station_id: Optional[int] = None) -> str:
        query = select(StationData)

        if station_id is not None:
            query = query.where(StationData.station_id == station_id)

        query = query.order_by(StationData.id.desc()).limit(1)
        async with session_maker() as session:
            result = (await session.scalars(query)).first()
            if not result:
                return "Database is empty" if station_id is None else f"Results for sensor {station_id}  not found"

            count = await session.scalar(select(func.count()).select_from(StationData))

        return _render_summary_template(result, count or 0)

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
