import json
from typing import Union

import requests

from .utils import GET_HEADERS, KEYWORDED_ARGUMENTS, POST_HEADERS


class Connection:
    def __init__(
        self,
        url: str,
        client_id: str = None,
        client_secret: str = None,
        username: str = None,
        password: str = None,
        api_port: int = None,
        scope: str = None,
        api_version: int = 4,
        access_token: str = None,
        refresh_token: str = None,
        admin_url: str = None,
        admin_port: int = None,
    ):
        """Initialize a connection between Python and a SigningHub REST API endpoint.

        What needs to be defined:
        - URL

        This can be combined with either:
        - A valid access token;
        - A combination of username, password, client_id and client_secret;
        - A refresh token with client_id and client_secret.

        Testing the configured URL can be either with an "about" call (which gets SigningHub instance information,
        no login required), or just fetching the URL, which should return a
        success.

        :param url: The API URL of the SigningHub instance
        :type url: str
        :param client_id: The client id of the integration in your SigningHub. Default value: None
        :type client_id: str
        :param client_secret: The client secret of the integration of your SigningHub. Default value: None
        :type client_secret: str
        :param username: The username of the user you want to authenticate with. Default value: None
        :type username: str
        :param password: The password of the given user. Default value: None
        :type password: str
        :param api_port: The port of the API instance. Default value: None
        :type api_port: int
        :param scope: The user email address we wish to scope with. Default value: None
        :type scope: str
        :param api_version:
            The version of the API of SigningHub. SigningHub version <=7.7.9: api_version = 3,
            SigningHub version >=7.7.9: api_version = 4
            Default value: None
        :type api_version: int
        :param access_token:
            A previously obtained access token which can be used in further calls.
            No authentication necessary if valid.
            Default value: None
        :type access_token: str
        :param refresh_token:
            A previously obtained refresh token (from a default authentication call) which can be used to authenticate
            with refresh token in combination of url, client_id and client_secret.
            Default value: None
        :type refresh_token: str
        """
        self.post_headers = POST_HEADERS
        self.get_headers = GET_HEADERS
        self._url = url
        self._client_id = client_id
        self._client_secret = client_secret
        self._username = username
        self._password = password
        self._scope = scope
        self._api_version = api_version
        self._api_port = api_port
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._x_change_password_token = None
        self._admin_url = admin_url
        self._admin_port = admin_port
        self._full_url = self.set_full_url()

    # Getters and setters
    @property
    def api_version(self):
        return self._api_version

    @property
    def url(self):
        return self._url

    @property
    def client_id(self):
        return self._client_id

    @property
    def client_secret(self):
        return self._client_secret

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def api_port(self):
        return self._api_port

    @property
    def scope(self):
        return self._scope

    @property
    def access_token(self):
        return self._access_token

    @property
    def refresh_token(self):
        return self._refresh_token

    @property
    def x_change_password_token(self):
        return self._x_change_password_token

    @property
    def admin_url(self):
        return self._admin_url

    @property
    def admin_port(self):
        return self._admin_port

    @property
    def full_url(self):
        return self._full_url

    @api_version.setter
    def api_version(self, new_api_version: int):
        if new_api_version not in (3, 4):
            raise ValueError("API version should be either 3 or 4")
        self._api_version = new_api_version

    @url.setter
    def url(self, new_url: str):
        self._url = new_url
        self._full_url = self.set_full_url()

    @client_id.setter
    def client_id(self, new_client_id: str):
        self._client_id = new_client_id

    @client_secret.setter
    def client_secret(self, new_client_secret: str):
        self._client_secret = new_client_secret

    @username.setter
    def username(self, new_username: str):
        self._username = new_username

    @password.setter
    def password(self, new_password: str):
        self._password = new_password

    @api_port.setter
    def api_port(self, new_api_port: int):
        self._api_port = new_api_port
        self._full_url = self.set_full_url()

    @scope.setter
    def scope(self, new_scope: str):
        self._scope = new_scope

    @access_token.setter
    def access_token(self, new_token: str):
        self._access_token = new_token

    @refresh_token.setter
    def refresh_token(self, new_refresh_token: str):
        self._refresh_token = new_refresh_token

    @admin_url.setter
    def admin_url(self, new_admin_url: str):
        self._admin_url = new_admin_url

    @admin_port.setter
    def admin_port(self, new_admin_port: int):
        self._admin_port = new_admin_port

    def set_full_url(self):
        if self.url.endswith("/"):
            self.url = self.url[:-1]
        if self.api_port:
            return f"{self.url}:{self.api_port}"
        return self.url

    # Documented SigningHub API Calls
    def authenticate(self) -> requests.models.Response:
        """Default authentication with username and password.

        When a status code 200 is received and thus the call succeeds, the _access_token attribute will receive
        the value of the 'access_token' parameter in the returned json body.
        If another status code than 200 is received and thus the call fails, the _access_token attribute will receive
        value None.

        :rtype: requests.models.Response
        """
        if (
            not self.full_url
            or not self.client_id
            or not self.client_secret
            or not self.username
            or not self.password
        ):
            raise ValueError(
                "URL, client ID, client secret, username and password cannot be None for default "
                "authentication"
            )
        url = f"{self.full_url}/authenticate"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "scope": self.scope,
        }
        response = requests.post(url, data, headers)
        try:
            if response.status_code == 200:
                self.access_token = json.loads(response.text).get("access_token", None)
                self.refresh_token = json.loads(response.text).get(
                    "refresh_token", None
                )
                self._x_change_password_token = response.headers.get(
                    "x-change-password", None
                )
        except:
            self.access_token = None
            self.refresh_token = None
            self._x_change_password_token = None
        finally:
            return response

    def authenticate_with_refresh_token(self) -> requests.models.Response:
        """Authenticating with configured refresh token.

        If the authentication succeeds, the _access_token attribute will be set to the received value.
        If the authentication fails or this function fails in some way, the _access_token attribute will be set to None.

        :rtype: requests.models.Response
        """
        if (
            not self.full_url
            or not self.client_id
            or not self.client_secret
            or not self.refresh_token
        ):
            raise ValueError(
                "URL, client ID, client secret and refresh token cannot be None"
            )
        url = f"{self.full_url}/authenticate"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "scope": self.scope,
        }
        response = requests.post(url, data, headers)
        try:
            self.access_token = json.loads(response.text).get("access_token")
            self.refresh_token = json.loads(response.text).get("refresh_token")
        except:
            self.access_token = None
        finally:
            return response

    def get_service_agreements(self) -> requests.models.Response:
        """Business applications can use this service API to get terms of services and privacy policy that are
        configured in SigningHub Admin console.

        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/terms"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def otp_login_authentication(
        self, mobile_number: str = None
    ) -> requests.models.Response:
        """SigningHub supports second factor authentication using OTP via SMS at login time via the web site GUI.
        Note this is different to OTP via SMS used in electronic signatures at the point of signing.
        This specifically refers to using the second factor authentication for SigningHub system access.

        To enable OTP via SMS second factor authentication see Enterprise Settings > Roles.

        At least one SMS provider must be configured in SigningHub administration in order to use this functionality.

        This API call is used to allow business applications to request an OTP via SMS to the user's mobile device
        for subsequent use in second factor authentication in the GUI.

        Note the mobile number is an optional field.  If not supplied, SigningHub will attempt to send the OTP to the
        mobile number stored in the user's Profile settings.
        If a mobile number is supplied in the call, then the OTP will be sent to this number,
        and any stored one under Profile settings will be ignored.

        In the event that no mobile number is supplied, nor found under the user's Profile settings,
        an error will be returned.

        :param mobile_number: Mobile number to send the SMS text message to
        :type mobile_number: str

        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/authentication/otp"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.post(
            url=url, headers=headers, data=json.dumps({"mobile_number": mobile_number})
        )

    # Enterprise Management

    def about_signinghub(self) -> requests.models.Response:
        """Get information about the SigningHub enterprise this call is executed to.

        :rtype: requests.models.Response
            Body contains JSON with SigningHub information:
                installation_name: The name configured for SigningHub installation.
                version: The exact version of SigningHub installation.
                build: The full build number of SigningHub installation.
                patents: The patents used by SigningHub product.
                copyright: The copyright statement by Ascertia Limited.
        """
        url = f"{self.full_url}/v{self.api_version}/about"
        headers = self.get_headers
        response = requests.get(url=url, headers=headers)
        return response

    def register_enterprise_user(
        self, user_email: str, user_name: str, **kwargs
    ) -> requests.models.Response:
        """Register a SigningHub user to your enterprise

        :param user_email: email address of the new account
        :type user_email: str
        :param user_name: username of the new account
        :type user_name: str
        :key job_title: str; job title of the new account
        :key company_name: str; company name of the new account
        :key mobile_number: str; mobile number of the new account
        :key user_password: str; password to be set for the new account
        :key security_question: str; security question of the new account
        :key security_answer: str; security answer of the new account
        :key enterprise_role: str; role of the new account
        :key email_notification: bool; whether or not the account should receive an email about the account creation
        :key country: str; country of the new account
        :key time_zone: str; timezone of the new account
        :key language: str; language of the new account
        :key user_ra_id: str; user ID of the user registered in SAM service inside SigningHub Engine (ADSS Server)
        :key user_csp_id: str; user ID of the user registered in CSP service inside SigningHub Engine (ADSS Server)
        :key certificate_alias: str; signing certificate identification for user signing certificate registered under certification service inside SigningHub Engine (ADSS Server)
        :key common_name: str; an identifiable name for the user that added as Common Name (CN) in identity certificate
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/users"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"user_email": user_email, "user_name": user_name}
        for attribute in KEYWORDED_ARGUMENTS["register_enterprise_user"]:
            if attribute in kwargs:
                data[attribute] = kwargs[attribute]
        return requests.post(url=url, data=json.dumps(data), headers=headers)

    def get_enterprise_users(self, **kwargs) -> requests.models.Response:
        """Get users within your enterprise

        :key x_search_text: str; this method will return all users who's email address contains the search string"""
        url = f"{self.full_url}/v{self.api_version}/enterprise/users"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        if "x_search_text" in kwargs:
            headers["x-search-text"] = kwargs["x_search_text"]
        return requests.get(url=url, headers=headers)

    def update_enterprise_user(
        self, user_email: str, **kwargs
    ) -> requests.models.Response:
        """Update the properties of a user within your enterprise

        :param user_email: email address of the user
        :type user_email: str
        :key user_name: str; new the new username of the enterprise user
        :key job_title: str; new job title of the enterprise user
        :key company_name: str; new company name of the enterprise user
        :key mobile_number: str; new mobile number of the enterprise user
        :key user_old_password: str; the old password of the enterprise user in case of password change
        :key user_new_password: str; the new password of the enterprise user in case of password change
        :key security_question: str; new security question of the enterprise user
        :key security_answer: str; new security answer of the enterprise user
        :key enterprise_role: str; new role for the enterprise user
        :key email_notification: bool; whether or not the account should receive an email about the account update
        :key country: str; new country of the enterprise user
        :key time_zone: str; new timezone of the enterprise user
        :key language: str; new language of the enterprise user
        :key user_ra_id: str; new user ID of the user registered in SAM service inside SigningHub Engine (ADSS Server)
        :key user_csp_id: str; new user ID of the user registered in CSP service inside SigningHub Engine (ADSS Server)
        :key certificate_alias: str; new signing certificate identification for user signing certificate registered under certification service inside SigningHub Engine (ADSS Server)
        :key common_name: str; new identifiable name for the user that added as Common Name (CN) in identity certificate

        :returns: HTTP response
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/users"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"user_email": user_email}
        for attribute in KEYWORDED_ARGUMENTS["update_enterprise_user"]:
            if attribute in kwargs:
                data[attribute] = kwargs[attribute]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def delete_enterprise_user(self, user_email: str) -> requests.models.Response:
        """Delete a user within which exists in your enterprise

        :param user_email: email address of the user that needs to be deleted
        :type user_email: str

        :returns: HTTP response
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/users"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.delete(
            url=url, headers=headers, data=json.dumps({"user_email": user_email})
        )

    def invite_enterprise_user(
        self, user_email: str, user_name: str, **kwargs
    ) -> requests.models.Response:
        """Invite an existing user to your enterprise

        :param user_email: email address of the user that needs to be invited
        :type user_email: str
        :key enterprise_role: role that needs to be given to the invited user. Defaults to the default role in your enterprise

        :returns: HTTP response
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/invitations"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"user_email": user_email, "user_name": user_name}
        if "enterprise_role" in kwargs:
            data["enterprise_role"] = kwargs["enterprise_role"]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def get_enterprise_invitations(
        self, page_number: int = 1, records_per_page: int = 10
    ) -> requests.models.Response:
        """Get all pending enterprise invitations

        :param page_number: which page needs to be given in the response body. Default = 1
        :type page_number: int
        :param records_per_page: how many records each page should contain in the response body. Default = 10
        :type records_per_page: int

        :returns: HTTP response
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/invitations/{page_number}/{records_per_page}"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def delete_enterprise_user_invitation(
        self, user_email: str
    ) -> requests.models.Response:
        """Delete an invitation to your enterprise

        :param user_email: email address to whom an invitation to your enterprise was sent and that needs te be deleted
        :type user_email: str

        :returns: HTTP response
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/invitations"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.delete(
            url=url, headers=headers, data=json.dumps({"user_email": user_email})
        )

    def get_enterprise_branding(self) -> requests.models.Response:
        """Get the branding of your enterprise.
        This included the logo in base64, the API URL to access this logo, the favicon in base64, the API URL to access this favicon,
        and the different color codes set in your enterprise

        :returns: HTTP response
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/branding"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        headers["x-base64"] = True
        return requests.get(url=url, headers=headers)

    def get_package(self, package_id: int) -> requests.models.Response:
        """Returns the info of a specific package

        :param package_id: ID of the package
        :type package_id: int

        :returns: HTTP response
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/packages/{package_id}"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def add_certificate(
        self,
        user_email: str,
        capacity_name: str,
        certificate_alias: str,
        level_of_assurance: str,
        key_protection_option: str,
        is_default: bool,
    ) -> requests.models.Response:
        """Add a certificate for a user within your enterprise

        :param user_email: email address of the user for whom the certificate needs to be added
        :type user_email: str
        :param capacity_name: friendly name for the certificate that has to be added for enterprise user.
        :type capacity_name: str
        :param certificate_alias: signing certificate identification for user signing certificate registered under certification service inside SigningHub Engine (ADSS Server)
        :type certificate_alias: str
        :param level_of_assurance: provide the level of assurance for a signing certificate, that you want to be used for this particular signing certificate. Possible values are ADVANCED_ELECTRONIC_SIGNATURE, HIGH_TRUST_ADVANCED and QUALIFIED_ELECTRONIC_SIGNATURE
        :type level_of_assurance: str
        :param key_protection_option: provide value if your signing certificate generated with a user password or the intended certificate generated for remote authorisation signing. Possible values are USER_PASSWORD and REMOTE_AUTHORISATION. Key protection option cannot be updated once it is set
        :type key_protection_option: str
        :param is_default: if true, the signing capacity set as default and show as selected on signing dialog
        :type is_default: bool

        :returns: HTTP response
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/signingcertificates"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = json.dumps(
            {
                "user_email": user_email,
                "capacity_name": capacity_name,
                "certificate_alias": certificate_alias,
                "level_of_assurance": level_of_assurance,
                "key_protection_option": key_protection_option,
                "isDefault": is_default,
            }
        )
        return requests.post(url=url, headers=headers, data=data)

    def update_certificate(
        self,
        certificate_id: int,
        user_email: str,
        capacity_name: str,
        certificate_alias: str,
        level_of_assurance: str,
        is_default: bool,
    ) -> requests.models.Response:
        """Update a certificate for a user within your enterprise

        :param certificate_id: certificate ID that needs to be removed for the user
        :type certificate_id: int
        :param user_email: email address of the user for whom the certificate needs to be updated
        :type user_email: str
        :param capacity_name: friendly name for the certificate that has to be updated for enterprise user.
        :type capacity_name: str
        :param certificate_alias: signing certificate identification for user signing certificate registered under certification service inside SigningHub Engine (ADSS Server)
        :type certificate_alias: str
        :param level_of_assurance: provide the level of assurance for a signing certificate, that you want to be used for this particular signing certificate. Possible values are ADVANCED_ELECTRONIC_SIGNATURE, HIGH_TRUST_ADVANCED and QUALIFIED_ELECTRONIC_SIGNATURE
        :type level_of_assurance: str
        :param is_default: if true, the signing capacity set as default and show as selected on signing dialog
        :type is_default: bool

        :returns: HTTP response
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/signingcertificates/{certificate_id}"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = json.dumps(
            {
                "user_email": user_email,
                "capacity_name": capacity_name,
                "certificate_alias": certificate_alias,
                "level_of_assurance": level_of_assurance,
                "isDefault": is_default,
            }
        )
        return requests.put(url=url, headers=headers, data=data)

    def delete_certificate(
        self, certificate_id: int, user_email: str
    ) -> requests.models.Response:
        """Removes a custom certificate for signing

        :param certificate_id: certificate ID that needs to be removed for the user
        :type certificate_id: int
        :param user_email: email address of the user for whom the certificate needs to be removed
        :type user_email: str

        :returns: HTTP response
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/signingcertificates/{certificate_id}"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.delete(
            url=url, headers=headers, data=json.dumps({"user_email": user_email})
        )

    def get_enterprise_group(self, group_id: int) -> requests.models.Response:
        """Get a specific enterprise group's details

        :param group_id: ID of the group
        :type group_id: int

        :returns: HTTP response
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/groups/{group_id}"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def add_enterprise_group(
        self, group_name: str, members: list, **kwargs
    ) -> requests.models.Response:
        """Add a new enterprise group

        :param group_name: name of the new group
        :type group_name: str
        :param members: users who should be added to this group. This list contains one or more dictionaries with 2 keys: "user_email" (the email address of the user to be added) and "user_name" (the username of the user to be added)
        :type members: list
        :key description: str; description of the enterprise group

        :returns: HTTP response
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/groups"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"name": group_name}
        data["members"] = members
        if "description" in kwargs:
            data["description"] = kwargs["description"]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def update_enterprise_group(
        self, group_id: int, **kwargs
    ) -> requests.models.Response:
        """Update an enterprise group

        :param group_id: ID of the group
        :type group_id: int
        :key name: str; new group name
        :key description: str; new group description
        :key members: list; new members of the group. The previous members will be replaced by this list which contains one or more dictionaries with 2 keys: "user_email" (the email address of the user to be added) and "user_name" (the username of the user to be added)

        :returns: HTTP response
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/groups/{group_id}"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = dict()

        for keyworded_argument in KEYWORDED_ARGUMENTS["update_enterprise_group"]:
            if keyworded_argument in kwargs:
                data[keyworded_argument] = kwargs[keyworded_argument]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def delete_enterprise_group(self, group_id: int) -> requests.models.Response:
        """Delete an enterprise group

        :param group_id: ID of the group
        :type group_id: int

        :returns: HTTP response
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/groups/{group_id}"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.delete(url=url, headers=headers)

    # Document Package

    def add_package(self, package_name: str, **kwargs) -> requests.models.Response:
        """Create a new package in SigningHub.

        :param package_name: Name of the package
        :type package_name: str
        :param kwargs:
            workflow_mode: str
                The workflow mode of the package, possible values are "ONLY_ME", "ME_AND_OTHERS" and "ONLY_OTHERS".
                If no workflow_mode is given, the default is used as per the settings in your SigningHub enterprise.
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"package_name": package_name}
        if "workflow_mode" in kwargs:
            data["workflow_mode"] = kwargs["workflow_mode"]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def rename_package(
        self, package_id: int, new_name: str
    ) -> requests.models.Response:
        """Rename a specific package.

        :param package_id: ID of the package to be renamed
        :type package_id: int
        :param new_name: New name of the package
        :param new_name: str
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.put(
            url=url, headers=headers, data=json.dumps({"package_name": new_name})
        )

    def upload_document(
        self,
        package_id: int,
        path_to_files_folder: str,
        file_name: str,
        x_source: str = "API",
        **kwargs,
    ) -> requests.models.Response:
        """Uploading a document to a specific package.

        :param package_id: ID of the package to which the document needs to be added.
        :type package_id: int
        :param path_to_files_folder: Absolute path of the file that needs to be uploaded.
        :type path_to_files_folder: str
        :param file_name: Name of the file.
        :type file_name: str
        :param x_source:
            This is the identification of the source of the document from where the document is uploaded, e.g. "My App".
        :type x_source: str

        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        headers["x-file-name"] = file_name
        headers["x-source"] = x_source
        if "x_convert_document" in kwargs:
            headers["x-convert-document"] = kwargs["x_convert_document"]
        return requests.post(
            url=url,
            headers=headers,
            data=open(path_to_files_folder + file_name, "rb").read(),
        )

    def apply_workflow_template(
        self, package_id: int, document_id: int, template_name: str, **kwargs
    ) -> requests.models.Response:
        """Applying a template on a document within a package.

        :param package_id: ID of the package the template should be applied to.
        :type package_id: int
        :param document_id: ID of the document within the package the template should be applied to.
        :type document_id: int
        :param template_name: Name of the template to be applied.
        :type template_name: str
        :param kwargs:
            apply_to_all: bool
                True if the template is to be applied on all documents within the package.
                False if not.
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/template"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"template_name": template_name}
        if "apply_to_all" in kwargs:
            data["apply_to_all"] = kwargs["apply_to_all"]
        return requests.post(url=url, data=json.dumps(data), headers=headers)

    def share_document_package(self, package_id: int) -> requests.models.Response:
        """Share a specific package.

        :param package_id: ID of the package to be shared.
        :type package_id: int
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.post(url=url, headers=headers)

    def change_document_package_owner(
        self, package_id: int, new_owner: str
    ) -> requests.models.Response:
        """Change the owner of a specific package.

        :param package_id: ID of the package
        :type package_id: int
        :param new_owner: email address of the account which should become the new owner
        :type new_owner: str"""
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/owner"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.put(
            url=url, headers=headers, data=json.dumps({"owner": new_owner})
        )

    def get_document_details(
        self, package_id: int, document_id: int
    ) -> requests.models.Response:
        """Get the details of a specific document.

        :param package_id: ID of the package
        :type package_id: int
        :param document_id: ID of the document
        :type document_id: int
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/details"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def get_document_image(
        self,
        package_id: int,
        document_id: int,
        resolution: str,
        page_number: int = 1,
        base_64=False,
        **kwargs,
    ) -> requests.models.Response:
        url = (
            f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}"
            f"/images/{page_number}/{resolution}"
        )
        if base_64:
            url += "/base64"
        headers = {
            "Accept": "image/png",
            "Authorization": "Bearer " + self.access_token,
        }
        if "x_password" in kwargs:
            headers["x-password"] = kwargs["x_password"]
        if "x_otp" in kwargs:
            headers["x-otp"] = kwargs["x_otp"]
        return requests.get(url=url, headers=headers)

    def download_document(
        self, package_id: int, document_id: str, base_64=False, **kwargs
    ) -> requests.models.Response:
        """Download a document.

        :param package_id: ID of the package where the document is located
        :type package_id: int
        :param document_id: ID of the document to be downloaded
        :type document_id: int
        :param base_64: whether or not the document should be downloaded in base64 format
        :type base_64: bool"""
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}"
        if base_64:
            url += "/base64"
        headers = {
            "Accept": "application/octet-stream",
            "Authorization": "Bearer " + self.access_token,
        }
        if "x_password" in kwargs:
            headers["x-password"] = kwargs["x_password"]
        if "x_otp" in kwargs:
            headers["x-otp"] = kwargs["x_otp"]
        return requests.get(url=url, headers=headers)

    def rename_document(
        self, package_id: int, document_id: int, new_document_name: str
    ) -> requests.models.Response:
        """Rename a specific document within a package.

        :param package_id: ID of the package in which the document is located.
        :type package_id: int
        :param document_id: ID of the document to be renamed.
        :type document_id: int
        :param new_document_name: New name for the document.
        :type new_document_name: str

        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.put(
            url=url,
            headers=headers,
            data=json.dumps({"document_name": new_document_name}),
        )

    def delete_document(
        self, package_id: int, document_id: int
    ) -> requests.models.Response:
        """Delete a specific document within a package.

        :param package_id: ID of the package where the document is in
        :type package_id: int
        :param document_id: ID of the document to be deleted
        :type document_id: int

        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.delete(url=url, headers=headers)

    def get_certify_policy_for_document(
        self, package_id: int, document_id: int
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/certify"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def update_certify_policy_for_document(
        self, package_id: int, document_id: int, enabled: bool, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/certify"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {
            "certify": {
                "enabled": enabled,
            }
        }
        if "permission" in kwargs:
            data["certify"]["permission"] = kwargs["permission"]
        if "lock_form_fields" in kwargs:
            data["lock_form_fields"] = kwargs["lock_form_fields"]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def get_package_verification(
        self, package_id: int, base_64=True
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/verification"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        headers["x-base64"] = base_64
        return requests.get(url=url, headers=headers)

    def get_document_verification(
        self, package_id: int, document_id: int, base_64=True
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/verification"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        headers["x-base64"] = base_64
        return requests.get(url=url, headers=headers)

    def change_document_order(
        self, package_id: int, document_id: int, new_document_order: int
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/reorder"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.put(
            url=url, headers=headers, data=json.dumps({"order": new_document_order})
        )

    def get_packages(
        self,
        document_status: str,
        page_number: int = 1,
        records_per_page: int = 10,
        **kwargs,
    ) -> requests.models.Response:
        """Get all packages of a specific user with a document status filter.

        :param document_status: str
            The status of the packages. Possible values include "ALL", "DRAFT", "PENDING", "SIGNED", "DECLINED",
            "INPROGRESS", "EDITED", "REVIEWED", "COMPLETED".
        :param page_number: int
            Page number of the returned info.
        :param records_per_page: int
            Number of records per page.
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{document_status}/{page_number}/{records_per_page}"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        if "x_search_text" in kwargs:
            headers["x-search-text"] = kwargs["x_search_text"]
        return requests.get(url=url, headers=headers)

    def delete_package(self, package_id: int) -> requests.models.Response:
        """Delete a specific package.

        :param package_id: int
            ID of the package to be deleted.
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.delete(url=url, headers=headers)

    def download_package(
        self, package_id: int, base_64=False, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}"
        if base_64:
            url += "/base64"
        headers = {
            "Accept": "application/octet-stream",
            "Authorization": "Bearer " + self.access_token,
        }
        if "x_password" in kwargs:
            headers["x-password"] = kwargs["x_password"]
        if "x_otp" in kwargs:
            headers["x-otp"] = kwargs["x_otp"]
        return requests.get(url=url, headers=headers)

    def open_document_package(
        self, package_id: int, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.full_url}/packages/{package_id}/open"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        if "x_password" in kwargs:
            headers["x-password"] = kwargs["x_password"]
        if "x_otp" in kwargs:
            headers["x-otp"] = kwargs["x_otp"]
        return requests.get(url=url, headers=headers)

    def close_document_package(self, package_id: int) -> requests.models.Response:
        url = f"{self.full_url}/v{self.full_url}/packages/{package_id}/close"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    # Document workflow

    def get_workflow_details(self, package_id: int) -> requests.models.Response:
        """Get the details of a specific workflow.

        :param package_id: Package ID of the package you want to get details on
        :type package_id: int
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def update_workflow_details(
        self, package_id: int, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = dict()
        for argument in KEYWORDED_ARGUMENTS["update_workflow_details"]:
            if argument in kwargs:
                data[argument] = kwargs[argument]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def get_workflow_history(self, package_id: int) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/log"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def get_workflow_history_details(
        self, package_id: int, log_id: int, base_64=True
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/log/{log_id}/details"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        headers["x-base64"] = base_64
        return requests.get(url=url, headers=headers)

    def get_certificate_saved_in_workflow_history(
        self, package_id: int, log_id: int, encryption_key: str
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/log/{log_id}/details/{encryption_key}"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def get_process_evidence_report(self, package_id: int) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/report"
        headers = {"Accept": "application/octet-stream"}
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def update_post_processing(self, package_id: int) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/post_process"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def add_users_to_workflow(
        self, package_id: int, user_email: str, user_name: str, role: str, **kwargs
    ) -> requests.models.Response:
        """Adding a user to a workflow.

        :param package_id: ID of the package the user should be added to.
        :type package_id: int
        :param user_email: email address of the user whom should be added
        :type user_email: str
        :param user_name: display name of the user to be added
        :type user_name: str
        :param role: role of the user in the workflow. Possible values include:  "SIGNER", "REVIEWER", "EDITOR", "CARBON_COPY" or "INPERSON_HOST"
        :type role: str
        :param kwargs:
            email_notification: (bool)(optional)
                If set to True, SigningHub will send notifications to the user via email as per the document owner
                and user notification settings.
                A value of False means no notifications will be sent to user throughout the workflow.
            signing_order: (int)(optional)
                Order of the recipient in the workflow.
                This signing order is mandatory when workflow type is "CUSTOM".
        :rtype: requests.models.Response
        """
        url = (
            f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/users"
        )
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = [
            {
                "user_email": user_email,
                "user_name": user_name,
                "role": role,
            }
        ]
        if "email_notification" in kwargs:
            data[0]["email_notification"] = kwargs["email_notification"]
        if "signing_order" in kwargs:
            data[0]["signing_order"] = kwargs["signing_order"]
        return requests.post(url=url, data=json.dumps(data), headers=headers)

    def update_workflow_user(
        self, package_id: int, order: int, **kwargs
    ) -> requests.models.Response:
        """Updating a workflow user.

        :param package_id: ID of the package in which the user should be updated.
        :type package_id: int
        :param order: Order of the user in the workflow.
        :type order: int
        :param kwargs:
            user_email: str
                New email address of the recipient to be updated.
            user_name: str
                New name of the recipient to be updated.
            role: str
                Role of the recipient to be updated. Possible values are "SIGNER", "REVIEWER", "EDITOR","CARBON_COPY"
                or "INPERSON_HOST". If no value is provided, old value will be retained.
                However, while XML type document preparation, only supported role types are "SIGNER",
                "REVIEWER" and "CARBON_COPY".
            email_notification: bool
                Setting its value to "true" sends an email notification to the user when its turn arrives in workflow.
                Setting its value to "false" does not send the email notification to the user on its turn.
                If no value is provided, old value will be retained.
            signing_order: int
                Order in which the workflow will be signed by the recipients.
                This signing order is important when workflow type is set to "CUSTOM".
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/{order}/user"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = dict()
        for argument in KEYWORDED_ARGUMENTS["update_workflow_user"]:
            if argument in kwargs:
                data[argument] = kwargs[argument]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def add_groups_to_workflow(
        self, package_id: int, group_name: str, **kwargs
    ) -> requests.models.Response:
        """Adding pre-defined groups to a package workflow.

        :param package_id: ID of the package the group should be added to.
        :type package_id: int
        :param group_name: Name of the group that should be added to the workflow.
        :type group_name: str
        :param kwargs:
            role: str
                role of the group as a recipient in the workflow. Possible value are "SIGNER",
                "REVIEWER", "EDITOR","CARBON_COPY" and "INPERSON_HOST".
                However, while XML type document preparation, only supported role types are "SIGNER", "REVIEWER"
                and "CARBON_COPY".
            email_notification: bool
                Setting its value to "true" sends an email notification to the user when its turn arrives in workflow.
                Setting its value to "false" does not send the email notification to the user on its turn.
                If no value is provided, default value of "true" will be set.
            signing_order: int
                Order in which the workflow will be signed by the recipients.
                This signing order is only important when workflow type is set to "CUSTOM".
        :rtype: requests.models.Response
        """
        url = (
            f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/groups"
        )
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"group_name": group_name}
        for argument in KEYWORDED_ARGUMENTS["add_groups_to_workflow"]:
            if argument in kwargs:
                data[argument] = kwargs[argument]
        payload = list()
        payload.append(data)
        return requests.post(url=url, headers=headers, data=json.dumps(payload))

    def update_workflow_group(
        self, package_id: int, order: int, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/enterprise/packages/{package_id}/workflow/{order}/group"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = dict()
        for argument in KEYWORDED_ARGUMENTS["update_workflow_group"]:
            if argument in kwargs:
                data[argument] = kwargs[argument]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def add_placeholder_to_workflow(
        self, package_id: int, placeholder_name: str, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/placeholder"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = [{"placeholder": placeholder_name}]
        for argument in KEYWORDED_ARGUMENTS["add_placeholder_to_workflow"]:
            if argument in kwargs:
                data[0][argument] = kwargs[argument]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def update_placeholder(
        self, package_id: int, order: int, **kwargs
    ) -> requests.models.Response:
        """Updating a placeholder on a workflow.
        Changeable properties include: placeholder name, role, email notifications, signing order.

        :param package_id: ID of the package in which you want to update the placeholder.
        :type package_id: int
        :param order: The order of the placeholder.
        :type order: int
        :param kwargs:
            placeholder: str
                Changing the name of the placeholder.
            role: str
                Changing the role of the placeholder. Options: "SIGNER", "REVIEWER", "EDITOR", "CARBON_COPY" and
                "INPERSON_HOST".
            email_notification: bool
                Setting its value to "true" sends an email notification to the user when its turn arrives in workflow.
                Setting its value to "false" does not send the email notification to the user on its turn.
                If no value is provided, old value will be retained.
            signing_order: int
                Order in which the workflow will be signed by the recipients.
                The signing order is only important when workflow type is set to "CUSTOM".
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/packages/{package_id}/workflow/{order}/placeholder"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = dict()
        for argument in KEYWORDED_ARGUMENTS["update_placeholder"]:
            if argument in kwargs:
                data[argument] = kwargs[argument]
        return requests.put(url=url, data=json.dumps(data), headers=headers)

    def get_workflow_users(self, package_id: int) -> requests.models.Response:
        url = (
            f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/users"
        )
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def update_workflow_users_order(
        self, package_id: int, old_order: int, new_order: int
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/{old_order}/reorder"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.put(
            url=url, headers=headers, data=json.dumps({"order": new_order})
        )

    def get_workflow_user_permissions(
        self, package_id: int, order: int
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/{order}/permissions"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def update_workflow_user_permissions(
        self, package_id: int, order: int, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/{order}/permissions"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"permissions": {"legal_notice": dict()}}
        if "apply_to_all" in kwargs:
            data["apply_to_all"] = kwargs["apply_to_all"]
        if "print" in kwargs:
            data["permissions"]["print"] = kwargs["print"]
        if "download" in kwargs:
            data["permissions"]["download"] = kwargs["download"]
        if "add_text" in kwargs:
            data["permissions"]["add_text"] = kwargs["add_text"]
        if "add_attachment" in kwargs:
            data["permissions"]["add_attachment"] = kwargs["add_attachment"]
        if "change_recipients" in kwargs:
            data["permissions"]["change_recipients"] = kwargs["change_recipients"]
        if "legal_notice_enabled" in kwargs:
            data["permissions"]["legal_notice"]["enabled"] = kwargs[
                "legal_notice_enabled"
            ]
        if "legal_notice_name" in kwargs:
            data["permissions"]["legal_notice"]["legal_notice_name"] = kwargs[
                "legal_notice_name"
            ]

        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def get_workflow_user_authentication_document_opening(
        self, package_id: int, order: int
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/{order}/authentication"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def update_workflow_user_authentication_document_opening(
        self, package_id: int, order: int, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/{order}/authentication"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {
            "authentication": {"password": dict(), "sms_otp": dict()},
            "access_duration": {
                "duration_by_date": {"duration": dict()},
                "duration_by_days": {"duration": dict()},
            },
        }
        if "apply_to_all" in kwargs:
            data["apply_to_all"] = kwargs["apply_to_all"]
        if "authentication_enabled" in kwargs:
            data["authentication"]["enabled"] = kwargs["authentication_enabled"]
        if "authentication_password_enabled" in kwargs:
            data["authentication"]["password"]["enabled"] = kwargs[
                "authentication_password_enabled"
            ]
        if "user_password" in kwargs:
            data["authentication"]["password"]["user_password"] = kwargs[
                "user_password"
            ]
        if "sms_otp_enabled" in kwargs:
            data["authentication"]["sms_otp"]["enabled"] = kwargs["sms_otp_enabled"]
        if "mobile_number" in kwargs:
            data["authentication"]["sms_otp"]["mobile_number"] = kwargs["mobile_number"]
        if "access_duration_enabled" in kwargs:
            data["access_duration_enabled"]["enabled"] = kwargs[
                "access_duration_enabled"
            ]
        if "access_duration_duration_by_date" in kwargs:
            data["access_duration_enabled"]["duration_by_date"]["enabled"] = kwargs[
                "access_duration_duration_by_date"
            ]
        if "access_duration_by_date_start_date_time" in kwargs:
            data["access_duration_enabled"]["duration_by_date"]["duration"][
                "start_date_time"
            ] = kwargs["access_duration_by_date_start_date_time"]
        if "access_duration_by_date_end_date_time" in kwargs:
            data["access_duration_enabled"]["duration_by_date"]["duration"][
                "end_date_time"
            ] = kwargs["access_duration_by_date_end_date_time"]
        if "access_duration_duration_by_days_enabled" in kwargs:
            data["access_duration_enabled"]["duration_by_days"]["enabled"] = kwargs[
                "access_duration_duration_by_days_enabled"
            ]
        if "access_duration_duration_by_days_total_days" in kwargs:
            data["access_duration_enabled"]["duration_by_days"]["duration"][
                "total_days"
            ] = kwargs["access_duration_duration_by_days_total_days"]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def delete_workflow_user(
        self, package_id: int, order: int
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/{order}"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.delete(url=url, headers=headers)

    def open_document_via_otp(
        self, package_id: int, order: int
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/{order}/authentication/otp"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.post(url=url, headers=headers)

    def open_document_via_password(
        self, package_id: int, order: int, password: str
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/{order}/authentication/password"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.post(
            url=url, headers=headers, data=json.dumps({"password": password})
        )

    def get_workflow_reminders(
        self, package_id: int, order: int
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/{order}/reminders"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def update_workflow_reminders(
        self, package_id: int, order: int, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow/{order}/reminders"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"repeat": dict()}
        if "apply_to_all" in kwargs:
            data["apply_to_all"] = kwargs["apply_to_all"]
        if "enabled" in kwargs:
            data["enabled"] = kwargs["enabled"]
        if "remind_after" in kwargs:
            data["remind_after"] = kwargs["remind_after"]
        if "repeat_enabled" in kwargs:
            data["repeat"]["enabled"] = kwargs["repeat_enabled"]
        if "keep_reminding_after" in kwargs:
            data["repeat"]["keep_reminding_after"] = kwargs["keep_reminding_after"]
        if "total_reminders" in kwargs:
            data["repeat"]["total_reminders"] = kwargs["total_reminders"]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def complete_workflow_in_the_middle(
        self, package_id: int
    ) -> requests.models.Response:
        """Set workflow status to COMPLETED when the workflow is not already COMPLETED.

        :param package_id: int
            Package ID of the workflow that needs to be completed.
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/enterprise/packages/{package_id}/complete"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.post(url=url, headers=headers)

    # Document Preparation

    def get_document_fields(
        self, package_id: int, document_id: int, page_number: Union[None, int] = None
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields"
        if page_number:
            url += f"/{page_number}"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def assign_document_field(
        self, package_id: int, document_id: int, field_name: str, order: int
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/assign"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.put(
            url=url,
            headers=headers,
            data=json.dumps([{"field_name": field_name, "order": order}]),
        )

    # This call is meant for API version 3 only. However, this will work on API version > 3 as well.
    def add_digital_signature_field(
        self, package_id: int, document_id: int, order: int, page_number: int, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/digital_signature"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"order": order, "page_no": page_number, "dimensions": dict()}
        if "field_name" in kwargs:
            data["field_name"] = kwargs["field_name"]
        if "display" in kwargs:
            data["display"] = kwargs["display"]
        if "x" in kwargs:
            data["dimensions"]["x"] = kwargs["x"]
        if "y" in kwargs:
            data["dimensions"]["y"] = kwargs["y"]
        if "width" in kwargs:
            data["dimensions"]["width"] = kwargs["width"]
        if "height" in kwargs:
            data["dimensions"]["height"] = kwargs["height"]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    # This call is meant for API version 3 only. However, this will work on API version 4 as well.
    def add_electronic_signature_field(
        self, package_id: int, document_id: int, order: int, page_no: int, **kwargs
    ) -> requests.models.Response:
        url = (
            f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}"
            f"/fields/electronic_signature"
        )
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {
            "order": order,
            "page_no": page_no,
            "dimensions": dict(),
            "authentication": {"enabled": False, "sms_otp": dict()},
        }
        if "field_name" in kwargs:
            data["field_name"] = kwargs["field_name"]
        if "display" in kwargs:
            data["display"] = kwargs["display"]
        if "x" in kwargs:
            data["dimensions"]["x"] = kwargs["x"]
        if "y" in kwargs:
            data["dimensions"]["y"] = kwargs["y"]
        if "width" in kwargs:
            data["dimensions"]["width"] = kwargs["width"]
        if "height" in kwargs:
            data["dimensions"]["height"] = kwargs["height"]
        if "authentication_enabled" in kwargs:
            data["authentication"]["enabled"] = kwargs["authentication_enabled"]
        if "authentication_sms_otp_enabled" in kwargs:
            data["authentication"]["sms_opt"]["enabled"] = kwargs[
                "authentication_sms_otp_enabled"
            ]
        if "mobile_number" in kwargs:
            data["authentication"]["sms_opt"]["mobile_number"] = kwargs["mobile_number"]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    # This call is meant for API version 4 (or higher).
    def add_signature_field(
        self, package_id: int, document_id: int, order: int, page_no: int, **kwargs
    ) -> requests.models.Response:
        if self.api_version < 4:
            raise ValueError("API version should be 4 or more recent")
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/signature"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"order": order, "page_no": page_no, "dimensions": dict()}
        for attribute in KEYWORDED_ARGUMENTS["add_signature_field"]:
            if attribute in kwargs:
                if attribute in ["x", "y", "width", "height"]:
                    data["dimensions"][attribute] = kwargs[attribute]
                else:
                    data[attribute] = kwargs[attribute]
        return requests.post(url=url, data=json.dumps(data), headers=headers)

    def add_in_person_field(
        self, package_id: int, document_id: int, order: int, page_number: int, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/in_person_signature"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"order": order, "page_no": page_number, "dimensions": dict()}
        for attribute in KEYWORDED_ARGUMENTS["add_in_person_field"]:
            if attribute in kwargs:
                if attribute in ["x", "y", "width", "height"]:
                    data["dimensions"][attribute] = kwargs[attribute]
                else:
                    data[attribute] = kwargs[attribute]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def add_initials_field(
        self, package_id: int, document_id: int, order: int, page_number: int, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/initials"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"order": order, "page_no": page_number, "dimensions": dict()}
        for attribute in KEYWORDED_ARGUMENTS["add_initials_field"]:
            if attribute in kwargs:
                if attribute in ["x", "y", "width", "height"]:
                    data["dimensions"][attribute] = kwargs[attribute]
                else:
                    data[attribute] = kwargs[attribute]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def add_textbox_field(
        self, package_id: int, document_id: int, order: int, page_number: int, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/text"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {
            "order": order,
            "page_no": page_number,
            "font": dict(),
            "dimensions": dict(),
        }
        if "field_name" in kwargs:
            data["field_name"] = kwargs["field_name"]
        if "type" in kwargs:
            data["type"] = kwargs["type"]
        if "format" in kwargs:
            data["format"] = kwargs["format"]
        if "placeholder" in kwargs:
            data["placeholder"] = kwargs["placeholder"]
        if "value" in kwargs:
            data["value"] = kwargs["value"]
        if "max_length" in kwargs:
            data["max_length"] = kwargs["max_length"]
        if "multiline" in kwargs:
            data["multiline"] = kwargs["multiline"]
        if "field_type" in kwargs:
            data["field_type"] = kwargs["field_type"]
        if "validation_rule" in kwargs:
            data["validation_rule"] = kwargs["validation_rule"]
        if "font_name" in kwargs:
            data["font"]["name"] = kwargs["font_name"]
        if "font_size" in kwargs:
            data["font"]["size"] = kwargs["font_size"]
        if "font_embedded_size" in kwargs:
            data["font"]["embedded_size"] = kwargs["font_embedded_size"]
        if "x" in kwargs:
            data["dimensions"]["x"] = kwargs["x"]
        if "y" in kwargs:
            data["dimensions"]["y"] = kwargs["y"]
        if "width" in kwargs:
            data["dimensions"]["width"] = kwargs["width"]
        if "height" in kwargs:
            data["dimensions"]["height"] = kwargs["height"]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def add_radiobox_field(
        self, package_id: int, document_id: int, order: int, page_number: int, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/radio"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"order": order, "page_no": page_number, "dimensions": dict()}
        if "field_name" in kwargs:
            data["field_name"] = kwargs["field_name"]
        if "value" in kwargs:
            data["value"] = kwargs["value"]
        if "validation_rule" in kwargs:
            data["validation_rule"] = kwargs["validation_rule"]
        if "radio_group_name" in kwargs:
            data["radio_group_name"] = kwargs["radio_group_name"]
        if "x" in kwargs:
            data["dimensions"]["x"] = kwargs["x"]
        if "y" in kwargs:
            data["dimensions"]["y"] = kwargs["y"]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def add_checkbox_field(
        self, package_id: int, document_id: int, order: int, page_number: int, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/checkbox"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"order": order, "page_no": page_number, "dimensions": dict()}
        if "field_name" in kwargs:
            data["field_name"] = kwargs["field_name"]
        if "value" in kwargs:
            data["value"] = kwargs["value"]
        if "validation_rule" in kwargs:
            data["validation_rule"] = kwargs["validation_rule"]
        if "x" in kwargs:
            data["dimensions"]["x"] = kwargs["x"]
        if "y" in kwargs:
            data["dimensions"]["y"] = kwargs["y"]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def autoplace_fields(
        self,
        package_id: int,
        document_id: int,
        search_text: str,
        order: int,
        field_type: str,
        **kwargs,
    ) -> requests.models.Response:
        """Automatically placing fields to a predefined string in the document.

        :param package_id: int
            ID of the package.
        :param document_id: int
            ID of the document on which the fields should be added.
        :param search_text: str
            Text to which the fields should be added on the document.
        :param order: int
            Order of the user to which the fields should be assigned.
        :param field_type: str
            Type of field to be created in the document. Possible values are "ELECTRONIC_SIGNATURE",
            "DIGITAL_SIGNATURE", "IN_PERSON_SIGNATURE", "INITIALS","TEXT", "NAME", "EMAIL", "COMPANY", "JOBTITLE",
            "RadioBox", "CheckBox", "DATE".
        :param kwargs:
            width: int
                Width of the field in pixels
            height: int
                Height of the field in pixels
            placement: str
                If the text is found, fields are to be placed in the document.
                Placement of the field can be mentioned in this attribute.
                Possible values of placement of a field are "LEFT", "RIGHT", "TOP", "BOTTOM".
                If no value is provided the default value will be "LEFT".
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/autoplace"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {
            "search_text": search_text,
            "order": order,
            "field_type": field_type,
            "dimensions": dict(),
            "font": dict(),
        }
        if "placement" in kwargs:
            data["placement"] = kwargs["placement"]
        if "level_of_assurance" in kwargs:
            if field_type != "SIGNATURE":
                raise ValueError(
                    f"Level of assurance cannot be given to field type {field_type}"
                )
            if self.api_version < 4:
                raise ValueError(
                    f"Level of assurance is not supported on API version < 4"
                )
            data["level_of_assurance"] = kwargs["level_of_assurance"]
        if "multiline" in kwargs:
            if field_type != "TEXT":
                raise ValueError(
                    f"Multiline option cannot be given for field type {field_type}"
                )
            data["multiline"] = kwargs["multiline"]
        if "value" in kwargs:
            if field_type not in ["TEXT", "RadioBox", "CheckBox"]:
                raise ValueError(f"Value cannot be assigned to field type {field_type}")
            data["value"] = kwargs["value"]
        if "max_length" in kwargs:
            if field_type in [
                "SIGNATURE",
                "DIGITAL_SIGNATURE",
                "ELECTRONIC_SIGNATURE",
                "RadioBox",
                "CheckBox",
            ]:
                raise ValueError(
                    f"max_length cannot be set for field type {field_type}"
                )
            data["field_type"] = kwargs["field_type"]
        if "validation_rule" in kwargs:
            if field_type not in ["CheckBox", "RadioBox"]:
                raise ValueError(
                    f"validation_rule cannot be set for field type {field_type}"
                )
            data["validation_rule"] = kwargs["validation_rule"]
        if "radio_group_name" in kwargs:
            if field_type != "RadioBox":
                raise ValueError(
                    f"radio_group_name cannot be set for field type {field_type}"
                )
            data["radio_group_name"] = kwargs["radio_group_name"]
        if "placeholder" in kwargs:
            if field_type != "IN_PERSON_SIGNATURE":
                raise ValueError(
                    f"Parameter placeholder cannot be set for field type {field_type}"
                )
            data["field_type"] = kwargs["field_type"]
        if "format" in kwargs:
            if field_type != "DATE":
                raise ValueError(
                    f"Parameter format cannot be set for field type {field_type}"
                )
            data["placeholder"] = kwargs["placeholder"]
        if "font_name" in kwargs:
            if field_type != "TEXT":
                raise ValueError(
                    f"Parameter font_name cannot be set for field type {field_type}"
                )
            data["font"]["name"] = kwargs["font_name"]
        if "font_size" in kwargs:
            if field_type != "TEXT":
                raise ValueError(
                    f"Parameter font_size cannot be set for field type {field_type}"
                )
            data["font"]["size"] = kwargs["font_size"]
        if "font_embedded_size" in kwargs:
            if field_type != "TEXT":
                raise ValueError(
                    f"Parameter font_embedded_size cannot be set for field type {field_type}"
                )
            data["font"]["embedded_size"] = kwargs["font_embedded_size"]
        if "width" in kwargs:
            data["dimensions"]["width"] = kwargs["width"]
        if "height" in kwargs:
            data["dimensions"]["height"] = kwargs["height"]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def update_digital_signature_field(
        self, package_id: int, document_id: int, field_name: str, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/digital_signature"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"field_name": field_name, "dimensions": dict()}
        if "renamed_as" in kwargs:
            data["renamed_as"] = kwargs["renamed_as"]
        if "page_number" in kwargs:
            data["page_no"] = kwargs["page_number"]
        if "display" in kwargs:
            data["display"] = kwargs["display"]
        if "x" in kwargs:
            data["dimensions"]["x"] = kwargs["x"]
        if "y" in kwargs:
            data["dimensions"]["y"] = kwargs["y"]
        if "width" in kwargs:
            data["dimensions"]["width"] = kwargs["width"]
        if "height" in kwargs:
            data["dimensions"]["height"] = kwargs["height"]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def update_electronic_signature_fields(
        self, package_id: int, document_id: int, field_name: str, **kwargs
    ) -> requests.models.Response:
        url = (
            f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}"
            f"/fields/electronic_signature"
        )
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {
            "field_name": field_name,
            "dimensions": dict(),
            "authentication": {"sms_otp": dict()},
        }
        if "renamed_as" in kwargs:
            data["renamed_as"] = kwargs["renamed_as"]
        if "display" in kwargs:
            data["display"] = kwargs["display"]
        if "page_number" in kwargs:
            data["page_no"] = kwargs["page_number"]
        if "x" in kwargs:
            data["dimensions"]["x"] = kwargs["x"]
        if "y" in kwargs:
            data["dimensions"]["y"] = kwargs["y"]
        if "width" in kwargs:
            data["dimensions"]["width"] = kwargs["width"]
        if "height" in kwargs:
            data["dimensions"]["height"] = kwargs["height"]
        if "authentication_enabled" in kwargs:
            data["authentication"]["enabled"] = kwargs["authentication_enabled"]
        if "authentication_sms_otp_enabled" in kwargs:
            data["authentication"]["sms_opt"]["enabled"] = kwargs[
                "authentication_sms_otp_enabled"
            ]
        if "mobile_number" in kwargs:
            data["authentication"]["sms_opt"]["mobile_number"] = kwargs["mobile_number"]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def update_in_person_field(
        self, package_id: int, document_id: int, field_name: str, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/in_person_signature"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {
            "field_name": field_name,
            "dimensions": dict(),
            "authentication": {"sms_otp": dict()},
        }
        if "renamed_as" in kwargs:
            data["renamed_as"] = kwargs["renamed_as"]
        if "page_number" in kwargs:
            data["page_no"] = kwargs["page_number"]
        if "placeholder" in kwargs:
            data["placeholder"] = kwargs["placeholder"]
        if "display" in kwargs:
            data["display"] = kwargs["display"]
        if "x" in kwargs:
            data["dimensions"]["x"] = kwargs["x"]
        if "y" in kwargs:
            data["dimensions"]["y"] = kwargs["y"]
        if "width" in kwargs:
            data["dimensions"]["width"] = kwargs["width"]
        if "height" in kwargs:
            data["dimensions"]["height"] = kwargs["height"]
        if "authentication_enabled" in kwargs:
            data["authentication"]["enabled"] = kwargs["authentication_enabled"]
        if "authentication_sms_otp_enabled" in kwargs:
            data["authentication"]["sms_opt"]["enabled"] = kwargs[
                "authentication_sms_otp_enabled"
            ]
        if "mobile_number" in kwargs:
            data["authentication"]["sms_opt"]["mobile_number"] = kwargs["mobile_number"]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def update_initials_field(
        self, package_id: int, document_id: int, field_name: str, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/initials"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"field_name": field_name, "dimensions": dict()}
        if "renamed_as" in kwargs:
            data["renamed_as"] = kwargs["renamed_as"]
        if "page_number" in kwargs:
            data["page_no"] = kwargs["page_number"]
        if "x" in kwargs:
            data["dimensions"]["x"] = kwargs["x"]
        if "y" in kwargs:
            data["dimensions"]["y"] = kwargs["y"]
        if "width" in kwargs:
            data["dimensions"]["width"] = kwargs["width"]
        if "height" in kwargs:
            data["dimensions"]["height"] = kwargs["height"]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def update_textbox_field(
        self, package_id: int, document_id: int, field_name: str, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/text"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"field_name": field_name, "font": dict(), "dimensions": dict()}
        for attribute in KEYWORDED_ARGUMENTS["update_textbox_field"]:
            if attribute in kwargs:
                if "font" in attribute:
                    data["font"][attribute[5:]] = kwargs[attribute]
                elif attribute in ["x", "y", "width", "height"]:
                    data["dimensions"][attribute] = kwargs[attribute]
                else:
                    data[attribute] = kwargs[attribute]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def update_radiobox_field(
        self, package_id: int, document_id: int, field_name: str, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/radio"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"field_name": field_name, "dimensions": dict()}
        if "renamed_as" in kwargs:
            data["renamed_as"] = kwargs["renamed_as"]
        if "page_number" in kwargs:
            data["page_no"] = kwargs["page_number"]
        if "value" in kwargs:
            data["value"] = kwargs["value"]
        if "validation_rule" in kwargs:
            data["validation_rule"] = kwargs["validation_rule"]
        if "radio_group_name" in kwargs:
            data["radio_group_name"] = kwargs["radio_group_name"]
        if "x" in kwargs:
            data["dimensions"]["x"] = kwargs["x"]
        if "y" in kwargs:
            data["dimensions"]["y"] = kwargs["y"]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def update_checkbox_field(
        self, package_id: int, document_id: int, field_name: str, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/checkbox"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"field_name": field_name, "dimensions": dict()}
        if "renamed_as" in kwargs:
            data["renamed_as"] = kwargs["renamed_as"]
        if "page_number" in kwargs:
            data["page_no"] = kwargs["page_number"]
        if "value" in kwargs:
            data["value"] = kwargs["value"]
        if "validation_rule" in kwargs:
            data["validation_rule"] = kwargs["validation_rule"]
        if "x" in kwargs:
            data["dimensions"]["x"] = kwargs["x"]
        if "y" in kwargs:
            data["dimensions"]["y"] = kwargs["y"]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def delete_document_field(
        self, package_id: int, document_id: int, field_name: str
    ) -> requests.models.Response:
        """Deleting a field from a document.

        :param package_id: ID of the package
        :type package_id: int
        :param document_id: ID of the document where the field is situated.
        :type document_id: int
        :param field_name: Name of the field which will be deleted.
        :type field_name: str
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.delete(
            url=url, data=json.dumps({"field_name": field_name}), headers=headers
        )

    def signer_authentication_via_otp(
        self, package_id: int, document_id: int, field_name: str
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/otp"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.post(
            url=url, headers=headers, data=json.dumps({"field_name": field_name})
        )

    def fill_initials(
        self,
        package_id: int,
        document_id: int,
        field_name: str,
        base64_image: bytes,
        **kwargs,
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/otp"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"field_name": field_name, "image": base64_image}
        if "apply_to_all" in kwargs:
            data["apply_to_all"] = kwargs["apply_to_all"]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def fill_form_fields(
        self,
        package_id: int,
        document_id: int,
        field_type: str,
        field_name: str,
        field_value,
        radio_group_name=None,
        **kwargs,
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {
            "text": list(),
            "radio": list(),
            "checkbox": list(),
            "dropdown": list(),
            "listbox": list(),
        }
        if "auto_save" in kwargs:
            data["auto_save"] = kwargs["auto_save"]
        if field_type in ["text", "radio", "checkbox", "dropdown", "listbox"]:
            field_data = {"field_name": field_name, "value": field_value}
            if field_type == "radio":
                if not radio_group_name:
                    raise ValueError(
                        f"Parameter 'radio_group_name' cannot be None when field type is set to "
                        f"'{field_type}'"
                    )
                field_data["radio_group_name"] = radio_group_name
            data[field_type].append(field_data)
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    # For API v4 and higher only.
    def sign_document_v4(
        self,
        package_id: int,
        document_id: int,
        field_name: str,
        hand_signature_image: str,
        signing_server: str,
        signing_capacity: str,
        **kwargs,
    ) -> requests.models.Response:
        """Sign a signature field. This function is for API version 4 (SigningHub version 7.7.9 and above).

        :param package_id: ID of the package
        :param document_id: ID of the document
        :param field_name: Name of the signature field to sign
        :param hand_signature_image: Image of the signature to set in base64
        :param signing_server: Name of the signing server of which to sign with
        :param signing_capacity: Name of the signing capacity to sign with
        :param kwargs:
            x-otp: OTP used as a second factor authentication for the signing operation
            signing_reason: Reason of signing provided by the recipient
            signing_location: Locale of the signing provided by the recipient
            contact_information: Contact information (mobile number) of the signer provided by the recipient
            user_name: Name of the signer
            user_password: Password of the user
            appearance_design: Name of the signature appearance to use. If none is provided, default setting will be
                used.
            skip_verification: If true: No signature verification returns in response body
        :rtype: requests.models.Response
        """
        if self.api_version < 4:
            raise ValueError(
                f"API version is set to {self.api_version}."
                f" This call can only be used for API version >= 4."
            )
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/sign"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {
            "field_name": field_name,
            "hand_signature_image": hand_signature_image,
            "signing_server": signing_server,
            "signing_capacity": signing_capacity,
        }
        if "x_otp" in kwargs:
            headers["x-otp"] = kwargs["x_otp"]
        for attribute in KEYWORDED_ARGUMENTS["sign_document_v4"]:
            if attribute in kwargs:
                data[attribute] = kwargs[attribute]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def sign_document_v3(
        self,
        package_id: int,
        document_id: int,
        field_name: str,
        hand_signature_image: str,
        **kwargs,
    ) -> requests.models.Response:
        """Sign a signature field. This function is for API version 3 (SigningHub version 7.7.9 and below).

        :param package_id: ID of the package
        :param document_id: ID of the document
        :param field_name: Name of the signature field to sign
        :param hand_signature_image: Image of the signature to set in base64
        :param kwargs:
            x-otp: OTP used as a second factor authentication for the signing operation
            signing_reason: Reason of signing provided by the recipient
            signing_location: Locale of the signing provided by the recipient
            contact_information: Contact information (mobile number) of the signer provided by the recipient
            user_name: Name of the signer
            user_password: Password of the user
            appearance_design: Name of the signature appearance to use. If none is provided, default setting will be
                used.
            signing_server: Name of the signing server of which to sign with
            signing_capacity: Name of the signing capacity to sign with
            skip_verification: If true: No signature verification returns in response body
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/sign"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"field_name": field_name, "hand_signature_image": hand_signature_image}
        if "x_otp" in kwargs:
            headers["x-otp"] = kwargs["x_otp"]
        for attribute in KEYWORDED_ARGUMENTS["sign_document_v3"]:
            if attribute in kwargs:
                data[attribute] = kwargs[attribute]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def decline_document(self, package_id: int, **kwargs) -> requests.models.Response:
        """Decline a pending package through the API

        :param package_id: ID of the package
        :type package_id: int
        :param kwargs:
            reason: Reason for the decline of the package
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/decline"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = dict()
        if "reason" in kwargs:
            data["reason"] = kwargs["reason"]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def approve_document(self, package_id: int, **kwargs) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/approve"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = dict()
        if "reason" in kwargs:
            data["reason"] = kwargs["reason"]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def submit_document(self, package_id: int) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/submit"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.post(url=url, headers=headers)

    def recall_document(self, package_id: int) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/workflow"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.delete(url=url, headers=headers)

    def finish_processing(self, package_id: int) -> requests.models.Response:
        """Within native SigningHub mobile apps and mobile web use cases,
        this call is necessary to ensure that each user completes their respective actions with respect to SigningHub.

        For example, after a signatory has signed a document in SigningHub App,
        this method is invoked by the application to ensure the workflow continues to process
        and the next signatory is notified, and the document status is available via the configured call-back URL.

        :param package_id: ID of the package that needs to be finished
        :type package_id: int
        :rtype: requests.models.Response
        """
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/finish"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.post(url=url, headers=headers)

    def get_registered_devices(self) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/authorization/devices"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def authorization_signing_request_status(
        self, package_id: int, document_id: int, field_name: str
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/field/status"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.post(
            url=url, headers=headers, data=json.dumps({"field_name": field_name})
        )

    # Account Management

    def register_user_free_trial(
        self, user_email: str, user_name: str, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"user_email": user_email, "user_name": user_name, "invitation": dict()}
        for attribute in KEYWORDED_ARGUMENTS["register_user_free_trial"]:
            if attribute in kwargs:
                data[attribute] = kwargs[attribute]
        if "invitation_to_enterprise_name" in kwargs:
            data["invitation"]["enterprise_name"] = data[
                "invitation_to_enterprise_name"
            ]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def get_account(self) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def get_account_password_policy(self) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account/password_policy"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.post(url=url, headers=headers)

    def get_user_role(self, base_64=True) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account/role"
        headers = self.get_headers
        headers["x-base64"] = base_64
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def resend_activation_email(self, user_email: str) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account/activation/resend"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.post(
            url=url, headers=headers, data=json.dumps({"user_email": user_email})
        )

    def send_forgot_password_request(self, user_email: str) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account/password/reset"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.post(
            url=url, headers=headers, data=json.dumps({"user_email": user_email})
        )

    def set_new_password(
        self, new_password: str, security_question: str, security_answer: str
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account/password/new"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = json.dumps(
            {
                "password": new_password,
                "security_question": security_question,
                "security_answer": security_answer,
            }
        )
        return requests.put(url=url, headers=headers, data=data)

    def get_account_invitations(self) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account/invitations"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.post(url=url, headers=headers)

    def accept_account_invitations(
        self, enterprise_name: str
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account/invitations"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.put(
            url=url,
            headers=headers,
            data=json.dumps({"enterprise_name": enterprise_name}),
        )

    def reject_all_account_invitations(self) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account/invitations"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.delete(url=url, headers=headers)

    def account_usage_statistics(self) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account/statistics/usage"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def document_statistics(self) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account/statistics/documents"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def get_notifications(
        self, records_per_page: int = 10, page_number: int = 1
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account/notifications/{records_per_page}/{page_number}"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def device_registration_for_push_notification(
        self, device_token: str, os_type: str
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/users/notifications/devices"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.post(
            url=url,
            headers=headers,
            data=json.dumps({"device_token": device_token, "os_type": os_type}),
        )

    def get_user_activity_logs(
        self, records_per_page: int = 10, page_number: int = 1
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account/log/{page_number}/{records_per_page}"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def get_user_activity_logs_details(
        self, log_id: int, base_64=True
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account/log/{log_id}/details"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        headers["x-base64"] = base_64
        return requests.get(url=url, headers=headers)

    def add_identity_for_a_user(
        self, user_email: str, provider: str, name: str, key: str, value: str
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/account/identity"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = json.dumps(
            {
                "user_email": user_email,
                "provider": provider,
                "name": name,
                "key": key,
                "value": value,
            }
        )
        return requests.post(url=url, headers=headers, data=data)

    # Personal Settings

    def get_general_profile_information(self):
        url = f"{self.full_url}/v{self.api_version}/settings/profile"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def update_general_profile_information(self, **kwargs) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/profile/general"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = dict()
        for attribute in KEYWORDED_ARGUMENTS["update_general_profile_information"]:
            if attribute in kwargs:
                data[attribute] = kwargs[attribute]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def change_password(
        self, old_password: str, new_password: str
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/profile/password"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = json.dumps(
            {"user_old_password": old_password, "user_new_password": new_password}
        )
        return requests.put(url=url, headers=headers, data=data)

    def get_profile_picture(self, base64=True) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/profile/general/photo"
        if base64:
            url += "/base64"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def update_profile_picture(
        self, profile_picture: bytes
    ) -> requests.models.Response:
        url = (
            f"{self.full_url}/v{self.api_version}/settings/profile/general/photo/base64"
        )
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.put(
            url=url, headers=headers, data=json.dumps({"photo": profile_picture})
        )

    def update_security_settings(
        self, password: str, security_question: str, security_answer: str
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/profile/security"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = json.dumps(
            {
                "password": password,
                "question": security_question,
                "answer": security_answer,
            }
        )
        return requests.put(url=url, headers=headers, data=data)

    def update_locale_settings(
        self, country: str, timezone: str, language: str
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/profile/locale"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = json.dumps(
            {"country": country, "timezone": timezone, "language": language}
        )
        return requests.put(url=url, headers=headers, data=data)

    def get_signature_settings(self, base_64=True) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/signatures"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        headers["x-base64"] = base_64
        return requests.get(url=url, headers=headers)

    def get_signature_appearance(self, signature_type: str) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/signatures/appearance/design/{signature_type}/preview"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def get_hand_signature_text_for_web(self) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/signatures/appearance/hand_signature/web/text"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def get_hand_signature_text_for_mobile(self) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/signatures/appearance/hand_signature/mobile/text"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def get_hand_signature_upload_for_web(self) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/signatures/appearance/hand_signature/web/upload"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def get_hand_signature_upload_for_mobile(self) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/signatures/appearance/hand_signature/mobile/upload"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def update_signature_appearance_design(
        self, default_design: str
    ) -> requests.models.Response:
        url = (
            f"{self.full_url}/v{self.api_version}/settings/signatures/appearance/design"
        )
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.put(
            url=url,
            headers=headers,
            data=json.dumps({"default_design": default_design}),
        )

    def update_signature_settings_metadata(
        self, signing_reason: str, signing_location: str, contact_information: str
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/signatures/metadata"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = json.dumps(
            {
                "signing_reason": signing_reason,
                "signing_location": signing_location,
                "contact_information": contact_information,
            }
        )
        return requests.put(url=url, headers=headers, data=data)

    def update_hand_signature_browser(
        self, default_method: str, upload_image: bytes, text_value: str
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/signatures/appearance/browser"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = json.dumps(
            {
                "default_method": default_method,
                "upload_image": upload_image,
                "text_value": text_value,
            }
        )
        return requests.put(url=url, headers=headers, data=data)

    def update_hand_signature_mobile(
        self, default_method: str, upload_image: bytes, text_value: str
    ) -> requests.models.Response:
        url = (
            f"{self.full_url}/v{self.api_version}/settings/signatures/appearance/mobile"
        )
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = json.dumps(
            {
                "default_method": default_method,
                "upload_image": upload_image,
                "text_value": text_value,
            }
        )
        return requests.put(url=url, headers=headers, data=data)

    def get_initials_for_upload_option(self) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/signatures/appearance/initials/upload"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def get_initials_for_text_option(self) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/signatures/appearance/initials/text"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def update_initial_appearance(
        self, default_method: str, upload_image: bytes, text_value: str
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/signatures/appearance/initials"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = json.dumps(
            {
                "default_method": default_method,
                "upload_image": upload_image,
                "text_value": text_value,
            }
        )
        return requests.put(url=url, headers=headers, data=data)

    def get_signature_delegation_settings(self) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/delegate"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def update_signature_delegation_settings(
        self, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/delegate"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"delegate": dict()}
        if "enabled" in kwargs:
            data["enabled"] = kwargs["enabled"]
        for attribute in KEYWORDED_ARGUMENTS["update_signature_delegation_settings"]:
            if attribute in kwargs:
                data["delegate"][attribute] = kwargs[attribute]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def add_contact(self, user_email: str, user_name: str) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/contacts"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        return requests.post(
            url=url,
            headers=headers,
            data=json.dumps({"user_email": user_email, "user_name": user_name}),
        )

    def get_contacts(
        self, records_per_page: int = 10, page_number: int = 1, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/contacts/{records_per_page}/{page_number}"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        if "x_search_text" in kwargs:
            headers["x-search-text"] = kwargs["x_search_text"]
        if "x_enterprise" in kwargs:
            headers["x-enterprise"] = kwargs["x_enterprise"]
        return requests.get(url=url, headers=headers)

    def get_groups(
        self, records_per_page: int = 10, page_number: int = 1, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/groups/{records_per_page}/{page_number}"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        if "x_search_text" in kwargs:
            headers["x-search-text"] = kwargs["x_search_text"]
        if "x_enterprise" in kwargs:
            headers["x-enterprise"] = kwargs["x_enterprise"]
        return requests.get(url=url, headers=headers)

    def get_library_documents(
        self, records_per_page: int = 10, page_number: int = 1, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/library/{records_per_page}/{page_number}"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        if "x_search_text" in kwargs:
            headers["x-search-text"] = kwargs["x_search_text"]
        if "x_enterprise" in kwargs:
            headers["x-enterprise"] = kwargs["x_enterprise"]
        return requests.get(url=url, headers=headers)

    def get_templates(
        self, records_per_page: int = 10, page_number: int = 1, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/templates/{records_per_page}/{page_number}"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        if "x_search_text" in kwargs:
            headers["x-search-text"] = kwargs["x_search_text"]
        if "x_enterprise" in kwargs:
            headers["x-enterprise"] = kwargs["x_enterprise"]
        return requests.get(url=url, headers=headers)

    def reset_email_notifications(self) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/notifications/email/reset"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.put(url=url, headers=headers)

    def get_personal_group(self, group_id: int) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/groups/{group_id}"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.get(url=url, headers=headers)

    def add_personal_group(
        self, group_name: str, members: list, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/groups"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = {"Name": group_name, "Members": members}
        if "description" in kwargs:
            data["Description"] = kwargs["description"]
        return requests.post(url=url, headers=headers, data=json.dumps(data))

    def update_personal_group(
        self, group_id: int, **kwargs
    ) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/groups/{group_id}"
        headers = self.post_headers
        headers = self.add_bearer(headers)
        data = dict()
        for attribute in KEYWORDED_ARGUMENTS["update_personal_group"]:
            if attribute in kwargs:
                data[attribute] = kwargs[attribute]
        return requests.put(url=url, headers=headers, data=json.dumps(data))

    def delete_personal_group(self, group_id: int) -> requests.models.Response:
        url = f"{self.full_url}/v{self.api_version}/settings/groups/{group_id}"
        headers = self.get_headers
        headers = self.add_bearer(headers)
        return requests.delete(url=url, headers=headers)

    def add_bearer(self, headers: dict) -> dict:
        headers["Authorization"] = f"Bearer {self.access_token}"
        return headers


def validate_dict(dictionary: dict):
    for key, value in dictionary.items():
        if not value:
            dictionary.pop(key)
    return dictionary
