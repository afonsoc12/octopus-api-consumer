from dataclasses import dataclass
from datetime import datetime


@dataclass
class _BaseClass:
    @property
    def measurement(self):
        return type(self).__name__


@dataclass
class Consumption(_BaseClass):
    """Consumption for an interval of time."""

    consumption: float
    interval_start: datetime
    interval_end: datetime
    serial_number: str

    @property
    def field_keys(self):
        return ["consumption", "interval_end"]

    @property
    def tag_keys(self):
        return ["serial_number"]

    @property
    def time_key(self):
        return "interval_start"


@dataclass
class ElectricityConsumption(Consumption):
    mpan: str
    unit: float = "kWh"

    @property
    def tag_keys(self):
        return super(ElectricityConsumption, self).tag_keys + list(
            self.__annotations__.keys()
        )


@dataclass
class GasConsumption(Consumption):
    mprn: int
    unit: float = "m³"

    @property
    def tag_keys(self):
        return super(GasConsumption, self).tag_keys + list(self.__annotations__.keys())
