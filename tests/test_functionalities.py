import unittest

from signinghubapi.signinghubapi import Connection


class TestRaiseIfWrongValue(unittest.TestCase):
    def test_wrong_api_version_value(self):
        conn = Connection(url="https://test.com")
        with self.assertRaises(ValueError):
            conn.api_version = 5


def test_url_ending_with_slash():
    conn = Connection(url="https://test.com/")
    assert conn.full_url == "https://test.com"

    conn.url = "https://test2.com/"
    assert conn.full_url == "https://test2.com"


def test_api_port():
    conn = Connection(url="https://test.com/", api_port=9999)
    assert conn.full_url == "https://test.com:9999"
    conn.api_port = None
    assert conn.full_url == "https://test.com"
    conn.api_port = 9999
    assert conn.full_url == "https://test.com:9999"

    conn = Connection(url="https://test.com/", api_port=None)
    conn.api_port = 9999
    assert conn.full_url == "https://test.com:9999"
    conn.api_port = None
    assert conn.full_url == "https://test.com"
