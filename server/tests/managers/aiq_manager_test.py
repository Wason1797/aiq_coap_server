from app.serializers.request import AiqDataFromStation
from app.types import AsyncSessionMaker
import pytest

from app.managers.aiq_manager import AiqDataManager


@pytest.mark.asyncio
async def test_save_sensor_data(main_db_session: AsyncSessionMaker, scd41_data_from_station: AiqDataFromStation) -> None:
    db_id = await AiqDataManager.save_sensor_data(main_db_session, scd41_data_from_station)

    data_in_db = await AiqDataManager.get_sensor_data_by_id(main_db_session, db_id)

    assert data_in_db is not None


@pytest.mark.asyncio
async def test_get_sensor_data_by_id():
    pass


@pytest.mark.asyncio
async def test_get_summary():
    pass


@pytest.mark.asyncio
async def test_get_summary_by_station_id():
    pass


@pytest.mark.asyncio
async def test_truncate_db():
    pass
