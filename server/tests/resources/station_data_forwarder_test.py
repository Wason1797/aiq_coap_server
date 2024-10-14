import pytest
from aiocoap import CHANGED  # type: ignore

from app.managers.aiq_manager import AiqDataManager
from app.resources.station_data_forwarder import StationDataForwarderResource
from app.types import AsyncSessionMaker


@pytest.mark.asyncio
async def test_render_put_in_br_from_end_device_no_backups(
    backup_db_session: AsyncSessionMaker,
    mock_payload_validator,
    mock_aiq_request_scd41_from_end_device,
    mock_station_id,
    mock_coap_client,
) -> None:
    border_router_id = 1
    result = await StationDataForwarderResource(
        backup_session=backup_db_session,
        payload_validator=mock_payload_validator,
        server_instance_id=border_router_id,
        coap_client=mock_coap_client,
        allow_backups=False,
    ).render_put(mock_aiq_request_scd41_from_end_device)

    mock_coap_client.put_payload.assert_awaited_once_with(
        f"{mock_aiq_request_scd41_from_end_device.payload.decode('ascii')}|{border_router_id}"
    )

    assert result.code == CHANGED

    summary_backup = await AiqDataManager.get_summary_by_station_id(backup_db_session, mock_station_id)

    assert "not found" in summary_backup


@pytest.mark.asyncio
async def test_render_put_in_br_from_end_device_with_backup(
    backup_db_session: AsyncSessionMaker,
    mock_payload_validator,
    mock_aiq_request_scd41_from_end_device,
    mock_station_id,
    mock_coap_client,
) -> None:
    border_router_id = 1
    result = await StationDataForwarderResource(
        backup_session=backup_db_session,
        coap_client=mock_coap_client,
        payload_validator=mock_payload_validator,
        server_instance_id=border_router_id,
        allow_backups=True,
    ).render_put(mock_aiq_request_scd41_from_end_device)

    mock_coap_client.put_payload.assert_awaited_once_with(
        f"{mock_aiq_request_scd41_from_end_device.payload.decode('ascii')}|{border_router_id}"
    )
    assert result.code == CHANGED

    summary_main = await AiqDataManager.get_summary_by_station_id(backup_db_session, mock_station_id)

    assert "not found" not in summary_main
