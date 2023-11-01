import os
from datetime import datetime
from unittest import mock

import pytest

from octopus_api_consumer.dataclasses import GasConsumption
from octopus_api_consumer.influx import InfluxDB


class TestInfluxDB:
    @pytest.fixture
    def consumption_point(self):
        return GasConsumption(
            consumption=50.0,
            interval_start=datetime(2023, 1, 1, 2, 0).isoformat(),
            interval_end=datetime(2023, 1, 1, 3, 0).isoformat(),
            serial_number="456789123",
            mprn=123456789,
            unit="m³",
        )

    @pytest.fixture
    def influx(self):
        mock_env = {
            "INFLUXDB_V2_BUCKET": "test_bucket",
            "INFLUXDB_V2_URL": "https://influxdb.my.domain.com",
            "INFLUXDB_V2_ORG": "test_org",
            "INFLUXDB_V2_TOKEN": "test_token",
        }
        with mock.patch.dict(os.environ, mock_env), mock.patch(
            "octopus_api_consumer.influx.InfluxDB.ready", return_value=True
        ):
            return InfluxDB()

    @mock.patch("influxdb_client.WriteApi.write")
    def test_write_consumptions_list(self, mock_write, influx, consumption_point):
        influx.write_consumptions([consumption_point])

        assert isinstance(mock_write.mock_calls[0].kwargs["record"], list)
        mock_write.assert_called_once_with(
            bucket=influx.bucket,
            record=[consumption_point],
            record_measurement_name="GasConsumption",
            record_time_key="interval_start",
            record_tag_keys=["serial_number", "mprn", "unit"],
            record_field_keys=["consumption", "interval_end"],
        )

    @mock.patch("influxdb_client.WriteApi.write")
    def test_write_consumptions_single_point(
        self, mock_write, influx, consumption_point
    ):
        influx.write_consumptions(consumption_point)
        assert isinstance(mock_write.mock_calls[0].kwargs["record"], list)

    @mock.patch("influxdb_client.InfluxDBClient.ping")
    def test_ping(self, mock_ping, influx):
        influx.ping()
        mock_ping.assert_called_once()

    @mock.patch("influxdb_client.InfluxDBClient.ready")
    def test_ready(self, mock_ready, influx):
        influx.ready()
        mock_ready.assert_called_once()
