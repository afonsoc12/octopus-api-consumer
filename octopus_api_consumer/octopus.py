import logging
import os
from datetime import datetime, timezone
from http.client import responses

import requests
from requests.auth import HTTPBasicAuth

from octopus_api_consumer.dataclasses import ElectricityConsumption


class Octopus:
    BASE_URL = "https://api.octopus.energy/"

    def __init__(self):
        self.__api_key = os.getenv("OCTOPUS_API_KEY")
        self.__electricity_mpan = os.getenv("OCTOPUS_ELECTRICITY_MPAN")
        self.__electricity_sn = os.getenv("OCTOPUS_ELECTRICITY_SN")
        self.__gas_mprn = os.getenv("OCTOPUS_GAS_MPRN")
        self.__gas_sn = os.getenv("OCTOPUS_GAS_SN")
        self.session = self._session()

    def consumption(self, url=None, period_from=None, period_to=None):
        if url:
            # URL override, in case it's a paginated request
            req = self._get(url=url)
        else:
            endpoint = f"/v1/electricity-meter-points/{self.__electricity_mpan}/meters/{self.__electricity_sn}/consumption"  # noqa E501
            parameters = {
                "period_from": period_from,
                "period_to": period_to,
                "page_size": 1000,
                "order_by": "period",
                "group_by": None,
            }
            if not period_from:
                logging.warning(
                    "A period_from was not provided. This will fetch the whole history"
                    " for the account. Might take some time..."
                )
            req = self._get(endpoint, params=parameters)

        try:
            req.raise_for_status()
            data = req.json()

            logging.debug(
                f"Got {data['count']} data points from"
                f" {data['results'][0]['interval_start']} to"
                f" {data['results'][-1]['interval_end']}"
            )

            consumption = [
                ElectricityConsumption(
                    **{
                        "mpan": self.__electricity_mpan,
                        "serial_number": self.__electricity_sn,
                        **cons,
                    }
                )
                for cons in data["results"]
            ]

            if data.get("next"):
                consumption += self.consumption(url=data.get("next"))

            return consumption

        except requests.exceptions.HTTPError:
            logging.error(f"Got error {req.status_code} {responses[req.status_code]}")
            if req.headers["Content-Type"] == "application/json":
                data = req.json()
                logging.error(f"Error body: {data}")
            raise

    def _session(self):
        s = requests.session()
        s.auth = HTTPBasicAuth(self.__api_key, "")

        def request_timestamp(r, *args, **kwargs):
            r.request_timestamp = datetime.strptime(
                r.headers.get("Date"), "%a, %d %b %Y %H:%M:%S %Z"
            ).replace(tzinfo=timezone.utc)
            return r

        s.hooks["response"].append(request_timestamp)

        return s

    def _get(self, endpoint=None, url=None, headers={}, params={}):
        if url:
            return self.session.get(url, headers=headers, params=params)
        elif endpoint:
            endpoint = endpoint[1:] if endpoint[0] == "/" else endpoint
            return self.session.get(
                self.BASE_URL + endpoint, headers=headers, params=params
            )
        else:
            raise AttributeError("Must specify either 'endpoint' or 'url' arguments.")
