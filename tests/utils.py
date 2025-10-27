from requests import HTTPError


class MockResponse:
    def __init__(self, status_code=200, json_dict={}, text=None, headers={}):
        self.status_code = status_code
        self.json_dict = json_dict
        self.text = text
        self.headers = headers

    def raise_for_status(self) -> None:
        if self.status_code >= 300:
            raise HTTPError()

    def json(self) -> dict:
        return self.json_dict
