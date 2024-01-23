from sqlalchemy import INTEGER, VARCHAR, PrimaryKeyConstraint
from sqlalchemy.orm import mapped_column, Mapped

from app.repositories.postgres.database import PostgresqlConnector


class SensorData(PostgresqlConnector.Base):
    __tablename__ = "sensor_data"

    id: Mapped[int] = mapped_column(INTEGER(), primary_key=True, autoincrement=True, nullable=False)
    co2: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    temperature: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    humidity: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    eco2: Mapped[int]
    tvoc: Mapped[int]
    aqi: Mapped[int]
    sensor_id: Mapped[int]
    timestamp: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    location_id: Mapped[str] = mapped_column(VARCHAR(36), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("id", name="pk_sensor_data"),)
