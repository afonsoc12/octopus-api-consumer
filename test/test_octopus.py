import os
import re
from datetime import datetime, timezone
from test.data import octopus_consumption as data
from unittest import mock

import pytest
import requests
import requests_mock

from octopus_api_consumer.dataclasses import ElectricityConsumption
from octopus_api_consumer.octopus import Octopus


class TestOctopus:
    @pytest.fixture
    def mock_adapter(self):
        return requests_mock.Adapter()

    @pytest.fixture
    def instance(self, mock_adapter):
        mock_env_vars = {
            "OCTOPUS_API_KEY": "mock_api_key",
            "OCTOPUS_ELECTRICITY_MPAN": "mock_e_mpan",
            "OCTOPUS_ELECTRICITY_SN": "mock_e_sn",
            # "OCTOPUS_GAS_MPRN": "",
            # "OCTOPUS_GAS_SN": ""
        }
        with mock.patch.dict(os.environ, mock_env_vars):
            o = Octopus()
            o.session.mount("https://", mock_adapter)
            return o

    def test_consumption_no_args(self, instance):
        expected_kwargs = {
            "period_from": None,
            "period_to": None,
            "page_size": 1000,
            "order_by": "period",
            "group_by": None,
        }
        resp = {
            "count": 123,
            "next": None,
            "results": [
                {
                    "consumption": 0.074,
                    "interval_start": "2023-01-15T23:30:00Z",
                    "interval_end": "2023-01-16T00:00:00Z",
                },
            ],
        }
        with mock.patch("requests.Session.get") as mock_get:
            mock_get.return_value.json = mock.Mock(return_value=resp)
            _ = instance.consumption()
            assert mock_get.call_count == 1
            assert mock_get.mock_calls[0].kwargs["params"] == expected_kwargs

    def test_consumption_recursive(self, instance, mock_adapter):
        with mock.patch.object(instance.session, "hooks", {}):
            mock_adapter.register_uri(
                "GET",
                re.compile(r"/.*\/consumption/?(\?.*)?$"),
                [{"json": data.response_one}, {"json": data.response_two}],
            )

            cons = instance.consumption()

            assert mock_adapter.call_count == 2
            assert "page=" not in mock_adapter.request_history[0].query
            assert "page=2" in mock_adapter.request_history[1].query
            assert cons == [
                ElectricityConsumption(
                    **{
                        "mpan": instance._Octopus__electricity_mpan,
                        "serial_number": instance._Octopus__electricity_sn,
                        **cons,
                    }
                )
                for cons in data.response_one["results"] + data.response_two["results"]
            ]

    def test_consumption_with_url(self, instance, mock_adapter):
        instance.session.mount("https://", mock_adapter)
        mock_adapter.register_uri(
            "GET", url=re.compile(r"/.*\/consumption/?(\?.*)?$"), json=data.response_two
        )

        path = "https://test.com/api/path/consumption"
        with mock.patch.object(instance.session, "hooks", {}), mock.patch.object(
            requests.Session, "get", wraps=instance.session.get
        ) as wrap_get:
            cons = instance.consumption(url=path)

            wrap_get.assert_called_once_with(path, headers={}, params={})
            assert cons == [
                ElectricityConsumption(
                    **{
                        "mpan": instance._Octopus__electricity_mpan,
                        "serial_number": instance._Octopus__electricity_sn,
                        **cons,
                    }
                )
                for cons in data.response_two["results"]
            ]

    def test_session_properties(self, instance):
        assert isinstance(instance.session, requests.Session)
        assert instance.session.auth.username == instance._Octopus__api_key
        assert instance.session.auth.password == ""

    def test_session_hooks(self, instance):
        headers = requests.structures.CaseInsensitiveDict()
        now = datetime.utcnow().astimezone(timezone.utc)
        headers["date"] = now.strftime("%a, %d %b %Y %H:%M:%S %Z")

        mock_adapter = requests_mock.Adapter()
        mock_adapter.register_uri("GET", "mock://test.com", headers=headers)
        instance.session.mount("mock://", mock_adapter)

        resp = instance.session.get("mock://test.com")
        assert resp.request_timestamp == now.replace(microsecond=0)

    def test_get_endpoint_slash(self, instance):
        with mock.patch("requests.Session.get") as mock_get:
            instance._get(endpoint="endpoint-a")
            instance._get(endpoint="/endpoint-a")
            assert mock_get.call_count == 2
            assert mock_get.mock_calls[0] == mock_get.mock_calls[1]

    def test_get_exc_no_url_and_endpoint(self, instance):
        with pytest.raises(
            AttributeError, match="Must specify either 'endpoint' or 'url' arguments"
        ):
            instance._get()
