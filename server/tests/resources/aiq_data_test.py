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
    mock_aiq_request_scd41_from_br,
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
        ).render_put(mock_aiq_request_scd41_from_br)

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
    mock_aiq_request_scd41_from_end_device,
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
        ).render_put(mock_aiq_request_scd41_from_end_device)

    assert result.code == CHANGED

    summary_main = await AiqDataManager.get_summary_by_station_id(main_db_session, mock_station_id)

    assert "not found" not in summary_main

    summary_backup = await AiqDataManager.get_summary_by_station_id(backup_db_session, mock_station_id)

    assert "not found" not in summary_backup


@pytest.mark.asyncio
async def test_render_put_in_br_from_end_device(
    main_db_session: AsyncSessionMaker,
    backup_db_session: AsyncSessionMaker,
    mock_payload_validator,
    mock_aiq_request_scd41_from_end_device,
    mock_management_bot,
    mock_station_id,
) -> None:
    with mock.patch("app.resources.aiq_data.ManagementBot", mock_management_bot):
        result = await AiqDataResource(
            is_main_server=False,
            main_session=main_db_session,
            backup_session=backup_db_session,
            coap_client=None,
            payload_validator=mock_payload_validator,
            allow_messages_from_br=False,
        ).render_put(mock_aiq_request_scd41_from_end_device)

    assert result.code == CHANGED

    summary_main = await AiqDataManager.get_summary_by_station_id(main_db_session, mock_station_id)

    assert "not found" not in summary_main


@pytest.mark.asyncio
async def test_render_put_in_br_from_end_device_with_forwarding(
    main_db_session: AsyncSessionMaker,
    backup_db_session: AsyncSessionMaker,
    mock_payload_validator,
    mock_aiq_request_scd41_from_end_device,
    mock_management_bot,
    mock_station_id,
    mock_coap_client,
) -> None:
    border_router_id = 1
    with mock.patch("app.resources.aiq_data.ManagementBot", mock_management_bot):
        result = await AiqDataResource(
            is_main_server=False,
            main_session=main_db_session,
            backup_session=backup_db_session,
            coap_client=mock_coap_client,
            payload_validator=mock_payload_validator,
            allow_messages_from_br=False,
            border_router_id=border_router_id,
        ).render_put(mock_aiq_request_scd41_from_end_device)

    mock_coap_client.put_payload.assert_awaited_once_with(
        f"{mock_aiq_request_scd41_from_end_device.payload.decode('ascii')}|{border_router_id}"
    )
    assert result.code == CHANGED

    summary_main = await AiqDataManager.get_summary_by_station_id(main_db_session, mock_station_id)

    assert "not found" not in summary_main
