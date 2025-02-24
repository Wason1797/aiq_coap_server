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
    nox: SensorData
    voc: SensorData


class BME688Data(BaseModel):
    hum: SensorData
    temp: SensorData
    press: SensorData
    gasres: SensorData


class SFA30Data(BaseModel):
    hco: SensorData
    temp: SensorData
    hum: SensorData


class AiqDataFromStation(BaseModel):
    scd41_d: Optional[SCD41Data] = None
    svm41_d: Optional[SVM41Data] = None
    ens160_d: Optional[ENS160Data] = None
    bme688_d: Optional[BME688Data] = None
    sfa30_d: Optional[SFA30Data] = None
    station_id: int
