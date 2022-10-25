import json


class MockResponse:
    def __init__(self, status_code=None, json=json.dumps({}), text=None, headers={}):
        self.status_code = status_code
        self.json = json
        self.text = text
        self.headers = headers
