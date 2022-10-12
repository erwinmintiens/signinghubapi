import json
from unittest.mock import patch

import requests
from signinghubapi.signinghubapi import Connection

from .utils import MockResponse


def test_about_signinghub_set_api_version():
    conn = Connection(url="https://testurl.com")
    with patch("signinghubapi.signinghubapi.requests.get") as mock_get:
        mock_get.return_value = MockResponse(
            status_code=200,
            text='{"installation_name": "SigningHub","version": "7.0.0.0","build": "6100.6100.280415.22852","patents": {"us_patent_no": "7,360,079"},"copyright": "Ascertia Limited. All rights reserved."}',
        )

        conn.about_signinghub(set_api_version=True)

    assert conn.api_version == 3

    with patch("signinghubapi.signinghubapi.requests.get") as mock_get:
        mock_get.return_value = MockResponse(
            status_code=200,
            text='{"installation_name": "SigningHub","version": "7.7.9.0","build": "6100.6100.280415.22852","patents": {"us_patent_no": "7,360,079"},"copyright": "Ascertia Limited. All rights reserved."}',
        )

        conn.about_signinghub(set_api_version=True)

    assert conn.api_version == 4


def test_about_signinghub_not_set_api_version():
    conn = Connection(url="https://testurl.com", api_version=3)
    with patch("signinghubapi.signinghubapi.requests.get") as mock_get:
        mock_get.return_value = MockResponse(
            status_code=200,
            text='{"installation_name": "SigningHub","version": "7.7.9.0","build": "6100.6100.280415.22852","patents": {"us_patent_no": "7,360,079"},"copyright": "Ascertia Limited. All rights reserved."}',
        )

        conn.about_signinghub(set_api_version=False)

    assert conn.api_version == 3
