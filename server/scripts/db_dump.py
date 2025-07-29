import asyncio
import csv
import datetime
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.env_manager import get_settings
from app.repositories.db.models import StationData
from app.repositories.mysql.database import MysqlConnector

EnvManager = get_settings()

CSV_HEADERS = (
    "id",
    "station_id",
    "station_name",
    "timestamp",
    "scd41_co2",
    "scd41_temperature",
    "scd41_humidity",
    "ens160_eco2",
    "ens160_tvoc",
    "ens160_aqi",
    "svm41_temperature",
    "svm41_humidity",
    "svm41_nox_index",
    "svm41_voc_index",
    "bme688_temperature",
    "bme688_humidity",
    "bme688_pressure",
    "bme688_gas_resistance",
    "sfa30_temperature",
    "sfa30_humidity",
    "sfa30_hco",
)


async def get_station_data_batch(session: AsyncSession, start_id: int, max_date: int) -> Sequence[StationData]:
    query = (
        select(StationData)
        .options(joinedload(StationData.station))
        .where(StationData.id > start_id)
        .where(StationData.timestamp < str(max_date))
        .order_by(StationData.id)
        .limit(1000)
    )

    return (await session.scalars(query)).all()


def str_number_to_float(num: str) -> float:
    return int(num) / 1000000


def station_data_to_dict(data: StationData) -> dict:
    scd41_data = {
        "scd41_co2": str_number_to_float(data.scd41_data.co2) if data.scd41_data else None,
        "scd41_temperature": str_number_to_float(data.scd41_data.temperature) if data.scd41_data else None,
        "scd41_humidity": str_number_to_float(data.scd41_data.humidity) if data.scd41_data else None,
    }

    ens160_data = {
        "ens160_eco2": data.ens160_data.eco2 if data.ens160_data else None,
        "ens160_tvoc": data.ens160_data.tvoc if data.ens160_data else None,
        "ens160_aqi": data.ens160_data.aqi if data.ens160_data else None,
    }

    svm41_data = {
        "svm41_temperature": str_number_to_float(data.svm41_data.temperature) if data.svm41_data else None,
        "svm41_humidity": str_number_to_float(data.svm41_data.humidity) if data.svm41_data else None,
        "svm41_nox_index": str_number_to_float(data.svm41_data.nox_index) if data.svm41_data else None,
        "svm41_voc_index": str_number_to_float(data.svm41_data.voc_index) if data.svm41_data else None,
    }

    bme688_data = {
        "bme688_temperature": str_number_to_float(data.bme688_data.temperature) if data.bme688_data else None,
        "bme688_humidity": str_number_to_float(data.bme688_data.humidity) if data.bme688_data else None,
        "bme688_pressure": str_number_to_float(data.bme688_data.pressure) if data.bme688_data else None,
        "bme688_gas_resistance": str_number_to_float(data.bme688_data.gas_resistance) if data.bme688_data else None,
    }

    sfa30_data = {
        "sfa30_temperature": str_number_to_float(data.sfa30_data.temperature) if data.sfa30_data else None,
        "sfa30_humidity": str_number_to_float(data.sfa30_data.humidity) if data.sfa30_data else None,
        "sfa30_hco": str_number_to_float(data.sfa30_data.hco) if data.sfa30_data else None,
    }

    return {
        "id": data.id,
        "station_id": data.station_id,
        "station_name": data.station.name,
        "timestamp": data.timestamp,
        **scd41_data,
        **ens160_data,
        **svm41_data,
        **bme688_data,
        **sfa30_data,
    }


async def main() -> None:
    MysqlConnector.init_db(EnvManager.get_backup_db_url())

    current_timestamp = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    print(f"Generating dump for database until {current_timestamp}")

    session = MysqlConnector.get_session()
    batch_id = -1

    with open(f"./dump_{current_timestamp}.csv", "a") as csv_dump:
        writer = csv.DictWriter(csv_dump, fieldnames=CSV_HEADERS)
        writer.writeheader()

        async with session as session:
            while len(batch := await get_station_data_batch(session, batch_id, current_timestamp)) > 0:
                writer.writerows(map(station_data_to_dict, batch))
                batch_id = batch[-1].id
                print(f"Wrote batch up to id: {batch_id}")


if __name__ == "__main__":
    asyncio.run(main())
