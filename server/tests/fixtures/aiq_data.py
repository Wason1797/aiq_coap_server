import pytest
import json

from typing import NamedTuple


class MockRequest(NamedTuple):
    payload: bytes


def _base_data(mock_station_id: int) -> dict:
    return {
        "scd41_d": {"co2": {"val1": 684, "val2": 0}, "temp": {"val1": 25, "val2": 50736}, "hum": {"val1": 49, "val2": 348449}},
        "station_id": mock_station_id,
    }


@pytest.fixture
def mock_station_id() -> int:
    return 1


@pytest.fixture
def mock_aiq_request_scd41_from_br(mock_station_id: int) -> MockRequest:
    """Don't forget to update the signature if you change the data"""

    return MockRequest(
        payload=f"{json.dumps(_base_data(mock_station_id)).replace(" ", "")}|b7288bcac962668e493e5eaf0feeb965007f4e75|1".encode(
            "ascii"
        )
    )


@pytest.fixture
def mock_aiq_request_scd41_from_end_device(mock_station_id: int) -> MockRequest:
    """Don't forget to update the signature if you change the data"""

    return MockRequest(
        payload=f"{json.dumps(_base_data(mock_station_id)).replace(" ", "")}|b7288bcac962668e493e5eaf0feeb965007f4e75".encode("ascii")
    )
