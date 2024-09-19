import pytest
from aiocoap import CHANGED

from app.resources.aiq_data import AiqDataResource
from app.types import AsyncSessionMaker

import unittest.mock as mock


@pytest.mark.asyncio
async def test_render_put_in_main_server(
    main_db_session: AsyncSessionMaker,
    backup_db_session: AsyncSessionMaker,
    mock_payload_validator,
    mock_aiq_request_scd41_main_server,
    mock_management_bot,
) -> None:
    with mock.patch("app.resources.aiq_data.ManagementBot", mock_management_bot):
        result = await AiqDataResource(
            is_main_server=True,
            main_session=main_db_session,
            backup_session=backup_db_session,
            coap_client=None,
            payload_validator=mock_payload_validator,
        ).render_put(mock_aiq_request_scd41_main_server)

    assert result.code == CHANGED
