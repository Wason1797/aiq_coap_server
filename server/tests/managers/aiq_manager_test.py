import pytest

from app.managers.aiq_manager import AiqDataManager
from app.serializers.request import AiqDataFromStation
from app.types import AsyncSessionMaker


@pytest.mark.asyncio
async def test_save_sensor_data(main_db_session: AsyncSessionMaker, full_data_from_station: AiqDataFromStation) -> None:
    db_id = await AiqDataManager.save_sensor_data(main_db_session, full_data_from_station)

    data_in_db = await AiqDataManager.get_sensor_data_by_id(main_db_session, db_id)

    assert data_in_db is not None
    assert data_in_db.scd41_data_id is not None


@pytest.mark.asyncio
async def test_get_sensor_data_by_id(main_db_session: AsyncSessionMaker, scd41_data_from_station: AiqDataFromStation):
    db_id = await AiqDataManager.save_sensor_data(main_db_session, scd41_data_from_station)

    data_in_db = await AiqDataManager.get_sensor_data_by_id(main_db_session, db_id)

    assert data_in_db is not None
    assert data_in_db.id == db_id


@pytest.mark.asyncio
async def test_get_summary(main_db_session: AsyncSessionMaker, scd41_data_from_station: AiqDataFromStation):
    await AiqDataManager.save_sensor_data(main_db_session, scd41_data_from_station)
    summary = await AiqDataManager.get_summary(main_db_session)

    assert summary is not None


@pytest.mark.asyncio
async def test_get_summary_with_full_data(main_db_session: AsyncSessionMaker, full_data_from_station: AiqDataFromStation):
    await AiqDataManager.save_sensor_data(main_db_session, full_data_from_station)
    summary = await AiqDataManager.get_summary(main_db_session)

    assert summary is not None
    assert "SCD41" in summary
    assert "SVM41" in summary
    assert "ENS160" in summary
    assert "BME688" in summary


@pytest.mark.asyncio
async def test_get_summary_by_station_id(main_db_session: AsyncSessionMaker, scd41_data_from_station: AiqDataFromStation):
    await AiqDataManager.save_sensor_data(main_db_session, scd41_data_from_station)
    null_summary = await AiqDataManager.get_summary_by_station_id(main_db_session, -1)
    assert "not found" in null_summary
    summary = await AiqDataManager.get_summary_by_station_id(
        main_db_session,
        scd41_data_from_station.station_id,
    )

    assert "not found" not in summary


@pytest.mark.asyncio
async def test_truncate_db(main_db_session: AsyncSessionMaker, scd41_data_from_station: AiqDataFromStation):
    db_id = await AiqDataManager.save_sensor_data(main_db_session, scd41_data_from_station)
    data_in_db = await AiqDataManager.get_sensor_data_by_id(main_db_session, db_id)

    assert data_in_db is not None

    await AiqDataManager.truncate_db(main_db_session)
    data_in_db = await AiqDataManager.get_sensor_data_by_id(main_db_session, db_id)
    assert data_in_db is None
