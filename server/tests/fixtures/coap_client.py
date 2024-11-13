from unittest.mock import MagicMock, AsyncMock
from aiocoap import CHANGED  # type: ignore

import pytest

from app.repositories.aiq_coap.client import CoapClient


@pytest.fixture(scope="function")
def mock_coap_client() -> MagicMock:
    mock_client = MagicMock(CoapClient)

    mock_client.put_payload = AsyncMock(return_value=CoapClient.Response(code=CHANGED, payload=""))
    mock_client.get_payload = AsyncMock(return_value=CoapClient.Response(code=CHANGED, payload=""))
    mock_client.delete_payload = AsyncMock(return_value=CoapClient.Response(code=CHANGED, payload=""))

    return mock_client
