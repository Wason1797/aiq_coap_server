import unittest.mock as mock

import pytest
from aiocoap import CHANGED  # type: ignore

from app.managers.aiq_manager import AiqDataManager
from app.resources.aiq_data import AiqDataResource
from app.types import AsyncSessionMaker


@pytest.mark.asyncio
async def test_render_put_in_main_server_from_br(
    main_db_session: AsyncSessionMaker,
    backup_db_session: AsyncSessionMaker,
    mock_payload_validator,
    mock_aiq_request_scd41_main_server_from_br,
    mock_management_bot,
    mock_station_id,
) -> None:
    with mock.patch("app.resources.aiq_data.ManagementBot", mock_management_bot):
        result = await AiqDataResource(
            is_main_server=True,
            main_session=main_db_session,
            backup_session=backup_db_session,
            coap_client=None,
            payload_validator=mock_payload_validator,
            allow_messages_from_br=True,
            allow_backups=True,
        ).render_put(mock_aiq_request_scd41_main_server_from_br)

    assert result.code == CHANGED

    summary_main = await AiqDataManager.get_summary_by_station_id(main_db_session, mock_station_id)

    assert "not found" not in summary_main

    summary_backup = await AiqDataManager.get_summary_by_station_id(backup_db_session, mock_station_id)

    assert "not found" not in summary_backup


@pytest.mark.asyncio
async def test_render_put_in_main_server_from_end_device(
    main_db_session: AsyncSessionMaker,
    backup_db_session: AsyncSessionMaker,
    mock_payload_validator,
    mock_aiq_request_scd41_main_server_from_end_device,
    mock_management_bot,
    mock_station_id,
) -> None:
    with mock.patch("app.resources.aiq_data.ManagementBot", mock_management_bot):
        result = await AiqDataResource(
            is_main_server=True,
            main_session=main_db_session,
            backup_session=backup_db_session,
            coap_client=None,
            payload_validator=mock_payload_validator,
            allow_messages_from_br=False,
            allow_backups=True,
        ).render_put(mock_aiq_request_scd41_main_server_from_end_device)

    assert result.code == CHANGED

    summary_main = await AiqDataManager.get_summary_by_station_id(main_db_session, mock_station_id)

    assert "not found" not in summary_main

    summary_backup = await AiqDataManager.get_summary_by_station_id(backup_db_session, mock_station_id)

    assert "not found" not in summary_backup
