from app.serializers.request import AiqDataFromStation
import pytest


@pytest.fixture
def scd41_data_from_station() -> AiqDataFromStation:
    return AiqDataFromStation.model_validate(
        {
            "scd41": {"temp": {"val1": 17, "val2": 0}, "co2": {"val1": 400, "val2": 0}, "hum": {"val1": 20, "val2": 0}},
            "station_id": 1,
        }
    )
