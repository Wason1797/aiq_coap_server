from typing import Optional
from pydantic import BaseModel


class SensorData(BaseModel):
    val1: int
    val2: int

    def to_str_number(self) -> str:
        return str(self.val1 * 1000000 + self.val2)


class SCD41Data(BaseModel):
    co2: SensorData
    temp: SensorData
    hum: SensorData


class ENS160Data(BaseModel):
    eco2: int
    tvoc: int
    aqi: int


class SVM41Data(BaseModel):
    temp: SensorData
    hum: SensorData
    noxi: SensorData
    voci: SensorData


class SPS30Data(BaseModel):
    pm1: SensorData
    pm25: SensorData
    pm10: SensorData
    tsize: SensorData


class AiqDataFromStation(BaseModel):
    scd41: Optional[SCD41Data] = None
    svm41: Optional[SVM41Data] = None
    ens160: Optional[ENS160Data] = None
    sps30: Optional[SPS30Data] = None
    station_id: int
