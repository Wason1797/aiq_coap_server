from app.serializers.request import AiqDataFromStation
import pytest


@pytest.fixture
def scd41_data_from_station() -> AiqDataFromStation:
    return AiqDataFromStation.model_validate(
        {
            "scd41_d": {"temp": {"val1": 17, "val2": 0}, "co2": {"val1": 400, "val2": 0}, "hum": {"val1": 20, "val2": 0}},
            "station_id": 1,
        }
    )


@pytest.fixture
def full_data_from_station() -> AiqDataFromStation:
    return AiqDataFromStation.model_validate(
        {
            "scd41_d": {"co2": {"val1": 542, "val2": 0}, "temp": {"val1": 24, "val2": 118791}, "hum": {"val1": 27, "val2": 774047}},
            "ens160_d": {"eco2": 554, "tvoc": 103, "aqi": 2},
            "bme688_d": {
                "gasres": {"val1": 12946860, "val2": 0},
                "press": {"val1": 101, "val2": 118000},
                "temp": {"val1": 28, "val2": 680000},
                "hum": {"val1": 18, "val2": 60000},
            },
            "svm41_d": {
                "temp": {"val1": 28, "val2": 680000},
                "hum": {"val1": 18, "val2": 60000},
                "nox": {"val1": 500, "val2": 0},
                "voc": {"val1": 400, "val2": 0},
            },
            "station_id": 1,
        }
    )
