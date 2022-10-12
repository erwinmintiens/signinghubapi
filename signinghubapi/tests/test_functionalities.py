import json
import unittest

import requests

from signinghubapi.signinghubapi import Connection
from signinghubapi.utils import GET_HEADERS_NO_AUTH

POST_HEADERS_NO_AUTH = {
    **GET_HEADERS_NO_AUTH,
    **{"Content-Type": "application/json"},
}


class TestRaiseIfWrongValue(unittest.TestCase):
    def test_wrong_api_version_value(self):
        conn = Connection(url="https://test.com")
        with self.assertRaises(ValueError):
            conn.api_version = 5
