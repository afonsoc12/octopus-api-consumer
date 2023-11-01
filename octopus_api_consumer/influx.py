import logging
import os

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


class InfluxDB:
    def __init__(self):
        self.bucket = os.getenv("INFLUXDB_V2_BUCKET", "octopus")
        self.client = InfluxDBClient.from_env_properties()

        try:
            status = self.ready()
            logging.info(f"Successfully connected to InfluxDB: {status}")
        except Exception:
            logging.error("Unable to connect to InfluxDB")
            raise

    def ping(self):
        """Ping InfluxDB database."""
        return self.client.ping()

    def ready(self):
        """Get status of InfluxDB database."""
        return self.client.ready()

    def write_consumptions(self, data_points):
        if not isinstance(data_points, list):
            data_points = [data_points]

        with self.client.write_api(write_options=SYNCHRONOUS) as write_api:
            write_api.write(
                bucket=self.bucket,
                record=data_points,
                record_measurement_name=data_points[0].measurement,
                record_time_key=data_points[0].time_key,
                record_tag_keys=data_points[0].tag_keys,
                record_field_keys=data_points[0].field_keys,
            )
