from datetime import datetime

import pytest

from octopus_api_consumer.dataclasses import (
    Consumption,
    ElectricityConsumption,
    GasConsumption,
    _BaseClass,
)


class TestBaseClass:
    def test_measurement(self):
        instance = _BaseClass()
        assert instance.measurement == "_BaseClass"


class TestConsumption:
    @pytest.fixture
    def instance(self):
        consumption_data = {
            "consumption": 100.0,
            "interval_start": datetime(2023, 1, 1, 0, 0),
            "interval_end": datetime(2023, 1, 1, 1, 0),
            "serial_number": "123456789",
        }
        return Consumption(**consumption_data)

    def test_instance(self, instance):
        assert isinstance(instance, Consumption)
        assert instance.measurement == "Consumption"

    def test_field_keys(self, instance):
        assert instance.field_keys == ["consumption", "interval_end"]

    def test_tag_keys(self, instance):
        assert instance.tag_keys == ["serial_number"]

    def test_time_key(self, instance):
        assert instance.time_key == "interval_start"


class TestElectricityConsumption:
    @pytest.fixture
    def instance(self):
        electricity_consumption_data = {
            "consumption": 200.0,
            "interval_start": datetime(2023, 1, 1, 1, 0),
            "interval_end": datetime(2023, 1, 1, 2, 0),
            "serial_number": "987654321",
            "mpan": "MPAN123",
            "unit": "kWh",
        }
        return ElectricityConsumption(**electricity_consumption_data)

    def test_instance(self, instance):
        assert isinstance(instance, ElectricityConsumption)
        assert instance.measurement == "ElectricityConsumption"


class TestGasConsumption:
    @pytest.fixture
    def instance(self):
        gas_consumption_data = {
            "consumption": 50.0,
            "interval_start": datetime(2023, 1, 1, 2, 0),
            "interval_end": datetime(2023, 1, 1, 3, 0),
            "serial_number": "456789123",
            "mprn": 123456789,
            "unit": "m³",
        }
        return GasConsumption(**gas_consumption_data)

    def test_instance(self, instance):
        assert isinstance(instance, GasConsumption)
        assert instance.measurement == "GasConsumption"

    def test_tag_keys(self, instance):
        assert instance.tag_keys == ["serial_number", "mprn", "unit"]
