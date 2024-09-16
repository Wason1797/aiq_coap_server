import pytest

from typing import NamedTuple


class TestBorderRouter(NamedTuple):
    ip_v4: str
    location: str


@pytest.fixture
def test_br_data():
    return TestBorderRouter("0.0.0.0", "test_location")
