import json

import requests

GET_HEADERS_NO_AUTH = {"Accept": "application/json"}


def get_and_set_api_version(resp: requests.Response, connection) -> None:
    """This function is used by the about_signinghub() call.
    This function is used to get the version of the configured connection URL and set the appropriate SH version.
    """
    if resp.status_code == 200 and "version" in json.loads(resp.text):
        sh_version = [int(x) for x in json.loads(resp.text)["version"].split(".")]
        if len(sh_version) == 4:
            if sh_version[0] >= 7 and sh_version[1] >= 7 and sh_version[2] >= 9:
                connection.api_version = 4
            else:
                connection.api_version = 3
        elif len(sh_version) < 4:
            connection.api_version = 4
        else:
            raise ValueError("Unknown length of version number")


def post_headers() -> dict:
    return {"Content-Type": "application/json", "Accept": "application/json"}


def get_headers() -> dict:
    return {"Accept": "application/json"}
