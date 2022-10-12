import json
from unittest.mock import patch

import pytest
import requests
from signinghubapi.signinghubapi import Connection

from .utils import MockResponse


@pytest.mark.parametrize(
    "version, result", [("7.0.0.0", 3), ("7.7.9.0", 4), ("8.2.4", 4)]
)
def test_about_signinghub_set_api_version(version, result):
    conn = Connection(url="https://testurl.com")
    with patch("signinghubapi.signinghubapi.requests.get") as mock_get:
        mock_get.return_value = MockResponse(
            status_code=200,
            text=json.dumps(
                {
                    "installation_name": "SigningHub",
                    "version": version,
                    "build": "6100.6100.280415.22852",
                    "patents": {"us_patent_no": "7,360,079"},
                    "copyright": "Ascertia Limited. All rights reserved.",
                }
            ),
        )

        conn.about_signinghub(set_api_version=True)


@pytest.mark.parametrize(
    "version, result", [("7.7.9.0", 3), ("8.2.4", 3), ("7.7.6", 4)]
)
def test_about_signinghub_not_set_api_version(version, result):
    conn = Connection(url="https://testurl.com", api_version=result)
    with patch("signinghubapi.signinghubapi.requests.get") as mock_get:
        mock_get.return_value = MockResponse(
            status_code=200,
            text=json.dumps(
                {
                    "installation_name": "SigningHub",
                    "version": version,
                    "build": "6100.6100.280415.22852",
                    "patents": {"us_patent_no": "7,360,079"},
                    "copyright": "Ascertia Limited. All rights reserved.",
                }
            ),
        )

        conn.about_signinghub(set_api_version=False)

    assert conn.api_version == result
