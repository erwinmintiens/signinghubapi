import json

import requests
from signinghubapi.signinghubapi import Connection
from signinghubapi.utils import GET_HEADERS_NO_AUTH

POST_HEADERS_NO_AUTH = {
    **GET_HEADERS_NO_AUTH,
    **{"Content-Type": "application/json"},
}


def test_headers():
    conn = Connection(url="testurl", access_token="test_access_token")

    headers = conn.get_headers(headers_type="get")
    assert headers == GET_HEADERS_NO_AUTH

    headers = conn.get_headers(headers_type="post")
    assert headers == POST_HEADERS_NO_AUTH

    headers = conn.get_headers(headers_type="get", authentication=True)
    assert headers == {
        **GET_HEADERS_NO_AUTH,
        **{"Authorization": f"Bearer {conn.access_token}"},
    }

    headers = conn.get_headers(headers_type="post", authentication=True)
    assert headers == {
        **POST_HEADERS_NO_AUTH,
        **{"Authorization": f"Bearer {conn.access_token}"},
    }
