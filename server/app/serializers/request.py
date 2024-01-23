from pydantic import BaseModel


class SensorData(BaseModel):
    val1: int
    val2: int

    def to_str_number(self) -> str:
        return str(self.val1 * 1000000 + self.val2)


class AiqDataFromStation(BaseModel):
    co2: SensorData
    temp: SensorData
    hum: SensorData
    eco2: int
    tvoc: int
    aqi: int
    sensor_id: int
