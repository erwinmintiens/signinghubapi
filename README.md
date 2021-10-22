# Description
[SigningHub](https://www.signinghub.com/) is a platform which is mainly used to sign documents with a digital or electronic signature.
On SigningHub, documents, users and settings can be uploaded and managed through the web view, as well as through the API.
This package focusses on the usage of said API through Python.

Signinghubapi package is the python integration of the SigningHub API. Most of the SigningHub API calls have been translated to python.

SigningHub API guide can be found [here](https://manuals.keysign.eu).

Both API v3 (SigningHub 7.7.9 and earlier) and API v4 (SigningHub 7.7.9 and above) have been integrated.

# Dependencies
This Python package depends on the ```requests``` module:

[Requests on PyPI](https://pypi.org/project/requests/)

[Requests on GitHub](https://github.com/psf/requests)

# Usage
Install this package with the command ```pip install signinghubapi```.

This package can be used to create a ```Connection``` object which connects to SigningHub.

Required parameters are:

- An URL;

Optional parameters are:
- An API connector client ID (Default value = None);
- An API connector client secret (Default value = None);
- A username (email address) to authenticate with (Default value = None);
- A password to authenticate with (Default value = None);
- A scope to authenticate with (Default value = None);
- An access token (Default value = None);
- A refresh token (Default value = None);
- An API version (3 or 4, depending on your SigningHub version. Default value = 3);
- An API port (if the API URL is not defined as a URL. Default value = None).

This object can execute the calls which are found in the API guide. These calls are translated to Python and the ```requests.models.Response``` object will be returned each time.

The validity of the provided URL can be tested with an ```about_signinghub()``` call. This call only requires the provided URL to work.

## Authentication
Authentication through API always need an API connector.
An API connector consists of a Client ID and a Client Secret.
Thus, the parameters ```client_id``` and ```client_secret``` should be provided to the ```Connection``` object.

### Authentication with username and password
Authentication through username and password can be achieved by settings the following parameters by the ```Connection``` object:
- Username (email address)
- Password

A bearer token will be received upon authentication, which will be automatically added to future calls with this object.

#### Example
```python
>>> from signinghubapi.signinghubapi import Connection
>>> conn = Connection(url='https://api.signinghub.com/', client_id='testclientid', client_secret='testclientsecret', username='test@email.com', password='1234')
>>> authentication = conn.authenticate()
>>> authentication.status_code
200
>>> authentication.text
'{"access_token":"LPAGaUoJ71Wi53vngCMty8i...'
```
### Authentication with refresh token
Upon successful authentication with username and password, a refresh token is returned aside from the access token.
This refresh token can be used to authenticate with in future calls.

#### Example
```python
>>> from signinghubapi.signinghubapi import Connection
>>> conn = Connection(url='https://api.signinghub.com/', client_id='testclientid', client_secret='testclientsecret', refresh_token='"QUVTMjU2LUdDTWLsQS+ByQscK...')
>>> authentication_with_refresh = conn.authenticate_with_refresh_token()
>>> authentication_with_refresh.status_code
200
>>> authentication_with_refresh.text
'{"access_token":"HTPk17blIEcjKIC_XCGe3cy4_kNCwp...'
```

## URL check example
```python
>>> from signinghubapi.signinghubapi import Connection
>>> conn = Connection(url='https://api.signinghub.com/', client_id='testclientid', client_secret='testclientsecret', username='test@email.com', password='1234')
>>> about = conn.about_signinghub()
>>> about.status_code
200
>>> about.text
'{"installation_name":"SigningHub","version":"7.7.8.26","build":"778...'
```
