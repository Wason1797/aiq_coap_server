import unittest.mock as mock

import pytest
from aiocoap import CHANGED  # type: ignore

from app.managers.aiq_manager import AiqDataManager
from app.resources.station_data_storage import StationDataStorageResource
from app.types import AsyncSessionMaker


@pytest.mark.asyncio
async def test_render_put_in_main_server_from_br(
    main_db_session: AsyncSessionMaker,
    backup_db_session: AsyncSessionMaker,
    mock_payload_validator,
    mock_aiq_request_scd41_from_br,
    mock_management_bot,
    mock_station_id,
) -> None:
    with mock.patch("app.resources.station_data_storage.ManagementBot", mock_management_bot):
        result = await StationDataStorageResource(
            main_session=main_db_session,
            backup_session=backup_db_session,
            payload_validator=mock_payload_validator,
            allow_backups=True,
        ).render_put(mock_aiq_request_scd41_from_br)

    assert result.code == CHANGED

    summary_main = await AiqDataManager.get_summary(main_db_session, mock_station_id)

    assert "not found" not in summary_main

    summary_backup = await AiqDataManager.get_summary(backup_db_session, mock_station_id)

    assert "not found" not in summary_backup


@pytest.mark.asyncio
async def test_render_put_in_main_server_from_end_device(
    main_db_session: AsyncSessionMaker,
    backup_db_session: AsyncSessionMaker,
    mock_payload_validator,
    mock_aiq_request_scd41_from_end_device,
    mock_management_bot,
    mock_station_id,
) -> None:
    with mock.patch("app.resources.station_data_storage.ManagementBot", mock_management_bot):
        result = await StationDataStorageResource(
            main_session=main_db_session,
            backup_session=backup_db_session,
            payload_validator=mock_payload_validator,
            allow_backups=True,
        ).render_put(mock_aiq_request_scd41_from_end_device)

    assert result.code == CHANGED

    summary_main = await AiqDataManager.get_summary(main_db_session, mock_station_id)

    assert "not found" not in summary_main

    summary_backup = await AiqDataManager.get_summary(backup_db_session, mock_station_id)

    assert "not found" not in summary_backup
