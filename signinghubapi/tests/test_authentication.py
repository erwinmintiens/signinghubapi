import json
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
            text=json.dumps(
                {
                    "access_token": "mock_access_token",
                    "token_type": "bearer",
                    "expires_in": 86399,
                    "refresh_token": "mock_refresh_token",
                }
            ),
        )

        response = conn.authenticate()

    assert conn.access_token == "mock_access_token"
    assert conn.refresh_token == "mock_refresh_token"
    assert response == mock_post.return_value


def test_authentication_json_error():
    conn = Connection(
        url="https://testurl.com",
        username="testuser",
        password="testpassword",
        client_id="testclientid",
        client_secret="testclientsecret",
        access_token="test-access-token",
        refresh_token="test-refresh-token",
    )
    with patch("signinghubapi.signinghubapi.requests.post") as mock_post:
        mock_post.return_value = MockResponse(
            status_code=200,
            text="This is not a valid json format",
        )

        response = conn.authenticate()

    assert conn.access_token == None
    assert conn.refresh_token == None
    assert conn._x_change_password_token == None
    assert response == mock_post.return_value
