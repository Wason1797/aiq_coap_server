from sqlalchemy import INTEGER, VARCHAR, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.repositories.db.connector import BaseDBConnector


class SCD41Data(BaseDBConnector.Base):
    __tablename__ = "scd41_data"

    id: Mapped[int] = mapped_column(INTEGER(), primary_key=True, autoincrement=True, nullable=False)
    co2: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    temperature: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    humidity: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("id", name="pk_scd41_data"),)


class ENS160Data(BaseDBConnector.Base):
    __tablename__ = "ens160_data"

    id: Mapped[int] = mapped_column(INTEGER(), primary_key=True, autoincrement=True, nullable=False)
    eco2: Mapped[int]
    tvoc: Mapped[int]
    aqi: Mapped[int]

    __table_args__ = (PrimaryKeyConstraint("id", name="pk_ens160_data"),)


class SVM41Data(BaseDBConnector.Base):
    __tablename__ = "svm41_data"

    id: Mapped[int] = mapped_column(INTEGER(), primary_key=True, autoincrement=True, nullable=False)
    temperature: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    humidity: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    nox_index: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    voc_index: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("id", name="pk_esvm41_data"),)


class StationData(BaseDBConnector.Base):
    __tablename__ = "station_data"

    id: Mapped[int] = mapped_column(INTEGER(), primary_key=True, autoincrement=True, nullable=False)

    scd41_data_id: Mapped[int] = mapped_column(INTEGER(), ForeignKey("scd41_data.id"), nullable=True)
    ens160_data_id: Mapped[int] = mapped_column(INTEGER(), ForeignKey("ens160_data.id"), nullable=True)
    svm41_data_id: Mapped[int] = mapped_column(INTEGER(), ForeignKey("svm41_data.id"), nullable=True)

    # Id of the individual sensor station submitting the data
    station_id: Mapped[int] = mapped_column(INTEGER(), ForeignKey("stations.id"), nullable=False)
    # Id of the border router forwarding the data
    border_router_id: Mapped[int] = mapped_column(INTEGER(), ForeignKey("border_routers.id"), nullable=True)

    timestamp: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)

    scd41_data: Mapped[SCD41Data] = relationship("SCD41Data", lazy="joined")
    ens160_data: Mapped[ENS160Data] = relationship("ENS160Data", lazy="joined")
    svm41_data: Mapped[ENS160Data] = relationship("SVM41Data", lazy="joined")

    __table_args__ = (PrimaryKeyConstraint("id", name="pk_station_data"),)


class BorderRouter(BaseDBConnector.Base):
    __tablename__ = "border_routers"

    id: Mapped[int] = mapped_column(INTEGER(), primary_key=True, autoincrement=True, nullable=False)
    ipv4_address: Mapped[str] = mapped_column(VARCHAR(25), nullable=False)
    location: Mapped[str] = mapped_column(VARCHAR(36), nullable=True, default=None)

    __table_args__ = (PrimaryKeyConstraint("id", name="pk_border_routers"),)


class Station(BaseDBConnector.Base):
    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(INTEGER(), primary_key=True, autoincrement=True, nullable=False)
    name: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("id", name="pk_stations"),)
