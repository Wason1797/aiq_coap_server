import pytest
import json

from typing import NamedTuple


class MockRequest(NamedTuple):
    payload: bytes


@pytest.fixture
def mock_station_id() -> int:
    return 1


@pytest.fixture
def mock_aiq_request_scd41_main_server(mock_station_id) -> MockRequest:
    """Don't forget to update the signature if you change the data"""

    base_data = {
        "scd41_d": {"co2": {"val1": 684, "val2": 0}, "temp": {"val1": 25, "val2": 50736}, "hum": {"val1": 49, "val2": 348449}},
        "station_id": mock_station_id,
    }
    return MockRequest(payload=f"{json.dumps(base_data).replace(" ", "")}|b7288bcac962668e493e5eaf0feeb965007f4e75|1".encode("ascii"))
