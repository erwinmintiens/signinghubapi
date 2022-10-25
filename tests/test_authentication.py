from unittest.mock import patch

import requests
from signinghubapi.signinghubapi import Connection

from .utils import MockResponse


def test_authentication_200():
    conn = Connection(
        url="https://testurl.com",
        username="testuser",
        password="testpassword",
        client_id="testclientid",
        client_secret="testclientsecret",
    )
    with patch("signinghubapi.signinghubapi.requests.post") as mock_post:
        mock_post.return_value = MockResponse(
            status_code=200,
            text='{"access_token": "mock_access_token","token_type": "bearer","expires_in": 86399,"refresh_token": "mock_refresh_token"}',
        )

        conn.authenticate()

    assert conn.access_token == "mock_access_token"
    assert conn.refresh_token == "mock_refresh_token"


def test_authentication_json_error():
    conn = Connection(
        url="https://testurl.com",
        username="testuser",
        password="testpassword",
        client_id="testclientid",
        client_secret="testclientsecret",
    )
    with patch("signinghubapi.signinghubapi.requests.post") as mock_post:
        mock_post.return_value = MockResponse(
            status_code=200,
            text="This is not a valid json format",
        )

        conn.authenticate()

    assert conn.access_token == None
    assert conn.refresh_token == None
