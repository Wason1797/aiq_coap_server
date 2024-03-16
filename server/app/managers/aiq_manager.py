from datetime import datetime
from typing import Callable

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.db.models import SensorData
from app.serializers.request import AiqDataFromStation

SUMMARY_TEMPLATE = """
Row Count: {}
co2: {} ppm
temp: {} C
hum: {} H%
aqi: {}
eco2: {} ppm
tvoc: {} ppb
sensor_id: {}
location_id: {}
"""


class AiqDataManager:
    @staticmethod
    async def save_sensor_data(session_maker: Callable[[], AsyncSession], data: AiqDataFromStation, location_id: str) -> None:
        async with session_maker() as session:
            session.add(
                SensorData(
                    co2=data.co2.to_str_number(),
                    temperature=data.temp.to_str_number(),
                    humidity=data.hum.to_str_number(),
                    eco2=data.eco2,
                    tvoc=data.tvoc,
                    aqi=data.aqi,
                    sensor_id=data.sensor_id,
                    timestamp=str(int(datetime.utcnow().timestamp())),
                    location_id=location_id,
                )
            )

            await session.commit()

    @staticmethod
    async def get_summary(session_maker: Callable[[], AsyncSession]) -> str:
        query = select(SensorData).order_by(SensorData.id.desc()).limit(1)
        async with session_maker() as session:
            result = (await session.scalars(query)).first()
            if not result:
                return "Database is empty"
            count = await session.scalar(select(func.count()).select_from(SensorData))
            return SUMMARY_TEMPLATE.format(
                count,
                int(result.co2) / 1000000,
                int(result.temperature) / 1000000,
                int(result.humidity) / 1000000,
                result.aqi,
                result.eco2,
                result.tvoc,
                result.sensor_id,
                result.location_id,
            )

    @staticmethod
    async def get_summary_by_sensor_and_location(session_maker: Callable[[], AsyncSession], sensor_id: int, location_id: str) -> str:
        query = (
            select(SensorData)
            .where(SensorData.sensor_id == sensor_id)
            .where(SensorData.location_id == location_id)
            .order_by(SensorData.id.desc())
            .limit(1)
        )

        async with session_maker() as session:
            result = (await session.scalars(query)).first()

            if not result:
                return f"Results for sensor {sensor_id} in location {location_id} not found"

            return SUMMARY_TEMPLATE.format(
                1,
                int(result.co2) / 1000000,
                int(result.temperature) / 1000000,
                int(result.humidity) / 1000000,
                result.aqi,
                result.eco2,
                result.tvoc,
                result.sensor_id,
                result.location_id,
            )

    @staticmethod
    async def truncate_db(session_maker: Callable[[], AsyncSession]) -> str:
        query = select(SensorData.id).order_by(SensorData.id.desc()).limit(120)
        async with session_maker() as session:
            ids = (await session.scalars(query)).all()
            if not ids:
                return "Database is empty"

            await session.execute(delete(SensorData).where(SensorData.id.in_(ids)))
            await session.commit()
        return "Truncate succesful"
