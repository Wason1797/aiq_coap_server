from pydantic import ValidationError
from app.serializers.request import AiqDataFromStation
from app.repositories.postgres.models import SensorData
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime


class AiqDataManager:
    @staticmethod
    async def save_sensor_data(session: AsyncSession, data: str) -> None:
        try:
            station_data = AiqDataFromStation.model_validate_json(data)
        except ValidationError:
            print("Error validatig payload")
            return

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
                    location_id="default",
                )
            )

            await session.commit()
