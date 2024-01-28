from datetime import datetime
from typing import Callable

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.serializers.request import AiqDataFromStation

from .models import SensorData

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
    async def save_sensor_data(session: AsyncSession, data: str, location_id: str) -> None:
        station_data = AiqDataFromStation.model_validate_json(data)

        async with session as session:
            session.add(
                SensorData(
                    co2=station_data.co2.to_str_number(),
                    temperature=station_data.temp.to_str_number(),
                    humidity=station_data.hum.to_str_number(),
                    eco2=station_data.eco2,
                    tvoc=station_data.tvoc,
                    aqi=station_data.aqi,
                    sensor_id=station_data.sensor_id,
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
