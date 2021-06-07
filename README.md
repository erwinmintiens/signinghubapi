# Description
[SigningHub](https://www.signinghub.com/) is a platform which is mainly used to sign documents with a digital or electronic signature.
On SigningHub, documents can be uploaded and managed through the web view, as well as through the API.
This package focusses on the usage of said API through Python.

Signinghubapi package is the python integration of the SigningHub API. Most of the SigningHub API calls have been translated to python.

SigningHub API guide can be found [here](https://manuals.keysign.eu).

Both API v3 (SigningHub 7.7.9 and earlier) and API v4 (SigningHub 7.7.9 and above) have been integrated.

# Dependencies
This Python package depends on the [requests](https://pypi.org/project/requests/) module.

# Usage
Install this package with the command ```pip install signinghubapi```.

This package can be used to create a ```Connection``` object which connects to SigningHub.

Required parameters are:
- An URL;
- An API connector client ID;
- An API connector client secret.

Optional parameters are:
- A username (email address) to authenticate with;
- A password to authenticate with;
- A scope to authenticate with;
- An access token;
- A refresh token;
- An API version (3 or 4, depending on your SigningHub version);
- An API port (if the API URL is not defined as a URL).

This object can execute the calls which are found in the API guide. These calls are translated to Python and the ```requests.Response``` object will be returned each time.

## Example
```python
from signinghubapi.signinghubapi import Connection

conn = Connection(url='https://sh-acc.keysign.eu/', client_id='testclientid', client_secret='testclientsecret', username='test@email.com', password='1234')

conn.about_signinghub()
conn.authenticate()
```
