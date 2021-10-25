import requests
import json


class Connection:
    def __init__(self, url: str, client_id: str = None, client_secret: str = None, username: str = None,
                 password: str = None, api_port: int = None, scope: str = None, api_version: int = 3,
                 access_token: str = None, refresh_token: str = None):
        """ Initialize a connection between Python and a SigningHub REST API endpoint.

        What needs to be defined:
        - URL

        This can be combined with either:
        - An valid access token;
        - A combination of username, password, client_id and client_secret;
        - A refresh token with client_id and client_secret.

        Testing the configured URL can be either with an "about" call (which gets SigningHub instance information,
        no login required), or just fetching the URL, which should return a
        success.

        :param url: str
            The API URL of the SigningHub instance
        :param client_id: str
            The client id of the integration in your SigningHub
        :param client_secret: str
            The client secret of the integration of your SigningHub
        :param username: str
            The username of the user you want to authenticate with
        :param password: str
            The password of the given user
        :param api_port: int
            The port of the API instance. Default value: None
        :param scope: str
            The user email address we wish to scope with. Default value: None
        :param api_version: int
            The version of the API of SigningHub. SigningHub version <=7.7.9: api_version = 3,
            SigningHub version >=7.7.9: api_version = 4
        :param access_token: str
            A previously obtained access token which can be used in further calls.
            No authentication necessary if valid.
        :param refresh_token: str
            A previously obtained refresh token (from a default authentication call) which can be used to authenticate
            with refresh token in combination of url, client_id and client_secret.
        """
        self._client_id = client_id
        self._client_secret = client_secret
        self._username = username
        self._password = password
        self._scope = scope
        self._api_version = api_version
        if api_port is None or api_port == "":
            if url.endswith("/"):
                self._url = url[:-1]
            else:
                self._url = url
        else:
            if url.endswith("/"):
                self._url = f"{url[:-1]}:{api_port}"
            else:
                self._url = f"{url}:{api_port}"
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._x_change_password_token = None

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

    @api_version.setter
    def api_version(self, new_api_version: int):
        self._api_version = new_api_version

    @url.setter
    def url(self, new_url: str, api_port=None):
        if new_url.endswith("/"):
            new_url = new_url[-1]
        if api_port is not None:
            self._url = new_url + ":" + str(api_port)
        else:
            self._url = new_url

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

    @scope.setter
    def scope(self, new_scope: str):
        self._scope = new_scope

    @access_token.setter
    def access_token(self, new_token: str):
        self._access_token = new_token

    @refresh_token.setter
    def refresh_token(self, new_refresh_token: str):
        self._refresh_token = new_refresh_token

    # Documented SigningHub API Calls
    def authenticate(self) -> requests.models.Response:
        """ Default authentication with username and password.

        When a status code 200 is received and thus the call succeeds, the _access_token attribute will receive
        the value of the 'access_token' parameter in the returned json body.
        If another status code than 200 is received and thus the call fails, the _access_token attribute will receive
        value None.

        :return: requests.models.Response
        """
        if not self.url or not self.client_id or not self.client_secret or not self.username or not self.password:
            raise ValueError("URL, client ID, client secret, username and password cannot be None for default "
                             "authentication")
        url = f"{self.url}/authenticate"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "scope": self.scope
        }
        authentication_call = requests.post(url, data, headers)
        try:
            authentication_text = json.loads(authentication_call.text)
            self.access_token = authentication_text['access_token']
            self.refresh_token = authentication_text['refresh_token']
            if 'x-change-password' in authentication_call.headers:
                self._x_change_password_token = authentication_call.headers['x-change-password']
        except:
            self.access_token = None
            self._x_change_password_token = None
        finally:
            return authentication_call

    def authenticate_with_refresh_token(self) -> requests.models.Response:
        """ Authenticating with configured refresh token.

        If the authentication succeeds, the _access_token attribute will be set to the received value.
        If the authentication fails or this function fails in some way, the _access_token attribute will be set to None.

        :return: requests.models.Response
        """
        if not self.url or not self.client_id or not self.client_secret or not self.refresh_token:
            raise ValueError("URL, client ID, client secret and refresh token cannot be None")
        url = f"{self.url}/authenticate"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'scope': self.scope
        }
        r = requests.post(url, data, headers)
        try:
            response_json = json.loads(r.text)
            self.access_token = response_json['access_token']
            self.refresh_token = response_json['refresh_token']
        except:
            self.access_token = None
        finally:
            return r

    def get_service_agreements(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/terms"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        return requests.get(url=url, headers=headers)

    def otp_login_authentication(self, mobile_number: str) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/authentication/otp"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'mobile_number': mobile_number
        })
        return requests.post(url=url, headers=headers, data=data)

    # Enterprise Management

    def about_signinghub(self) -> requests.models.Response:
        """ Get information about the SigningHub enterprise this call is executed to.

        :return: requests.models.Response
            Body contains JSON with SigningHub information:
                installation_name: The name configured for SigningHub installation.
                version: The exact version of SigningHub installation.
                build: The full build number of SigningHub installation.
                patents: The patents used by SigningHub product.
                copyright: The copyright statement by Ascertia Limited.
        """
        url = f"{self.url}/v{self.api_version}/about"
        headers = {
            'Accept': 'application/json'
        }
        return requests.get(url=url, headers=headers)

    def register_enterprise_user(self, user_email: str, user_name: str, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/users"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'user_email': user_email,
            'user_name': user_name
        }
        keyworded_attributes = ['job_title', 'company_name', 'mobile_number', 'user_password', 'security_question',
                                'security_answer', 'enterprise_role', 'email_notification', 'country', 'time_zone',
                                'language', 'user_ra_id', 'user_csp_id', 'certificate_alias', 'common_name']
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                data[attribute] = kwargs[attribute]
        data = json.dumps(data)
        return requests.post(url=url, data=data, headers=headers)

    def get_enterprise_users(self, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/users"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        if 'x-search-text' in kwargs:
            headers['x-search-text'] = kwargs['x-search-text']
        return requests.get(url=url, headers=headers)

    def update_enterprise_user(self, user_email: str, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/users"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            "user_email": user_email
        }
        keyworded_attributes = ['user_name', 'job_title', 'company_name', 'mobile_number', 'user_old_password',
                                'user_new_password', 'security_question', 'security_answer', 'enterprise_role',
                                'email_notification', 'enabled', 'country', 'time_zone', 'language', 'user_ra_id',
                                'user_csp_id', 'certificate_alias', 'common_name']
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                data[attribute] = kwargs[attribute]
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def delete_enterprise_user(self, user_email: str) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/users"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'user_email': user_email
        })
        return requests.delete(url=url, headers=headers, data=data)

    def invite_enterprise_user(self, user_email: str, user_name: str, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/invitations"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'user_email': user_email,
            'user_name': user_name
        }
        if 'enterprise_role' in kwargs:
            data['enterprise_role'] = kwargs['enterprise_role']
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def get_enterprise_invitations(self, page_number: int, records_per_page: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/invitations/{page_number}/{records_per_page}"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def delete_enterprise_user_invitation(self, user_email: str) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/invitations"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({'user_email': user_email})
        return requests.delete(url=url, headers=headers, data=data)

    def get_enterprise_branding(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/branding"
        headers = {
            'Accept': 'application/json',
            'x-base64': True,
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def get_package(self, package_id: int) -> requests.models.Response:
        """ Returns the info of a specific package.

        :param package_id: int
            ID of the package.
        :return: requests.models.Response
            JSON body contains:
                package_id,
                package_name,
                package_owner,
                owner_name,
                package_status,
                folder,
                unread,
                next_signer,
                next_signer_email:
                    user_email,
                    user_name,
                uploaded_on,
                modified_on
        """
        url = f"{self.url}/v{self.api_version}/enterprise/packages/{package_id}"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def add_certificate(self, user_email: str, capacity_name: str, certificate_alias: str, level_of_assurance: str,
                        key_protection_option: str, is_default: bool) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/signingcertificates"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'user_email': user_email,
            'capacity_name': capacity_name,
            'certificate_alias': certificate_alias,
            'level_of_assurance': level_of_assurance,
            'key_protection_option': key_protection_option,
            'isDefault': is_default
        })
        return requests.post(url=url, headers=headers, data=data)

    def update_certificate(self, certificate_id: int, user_email: str, capacity_name: str, certificate_alias: str,
                           level_of_assurance: str, is_default: bool) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/signingcertificates/{certificate_id}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'user_email': user_email,
            'capacity_name': capacity_name,
            'certificate_alias': certificate_alias,
            'level_of_assurance': level_of_assurance,
            'isDefault': is_default
        })
        return requests.put(url=url, headers=headers, data=data)

    def delete_certificate(self, certificate_id: int, user_email: str) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/signingcertificates/{certificate_id}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'user_email': user_email
        })
        return requests.delete(url=url, headers=headers, data=data)

    def get_enterprise_group(self, group_id: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/groups/{group_id}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def add_enterprise_group(self, group_name: str, members: list, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/groups"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            "Name": group_name,
            "Members": list()
        }
        for member in members:
            data['Members'].append(member)
        if 'description' in kwargs:
            data["Description"] = kwargs['description']
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def update_enterprise_group(self, group_id: int, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/groups/{group_id}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = dict()
        if 'name' in kwargs:
            data['Name'] = kwargs['name']
        if 'description' in kwargs:
            data['Description'] = kwargs['description']
        if 'members' in kwargs:
            if type(kwargs['members']) is list:
                data['Members'] = list()
                for member in kwargs['members']:
                    data['Members'].append(member)
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def delete_enterprise_group(self, group_id: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/groups/{group_id}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.delete(url=url, headers=headers)

    # Document Package

    def add_package(self, package_name: str, **kwargs) -> requests.models.Response:
        """ Create a new package in SigningHub.

        :param package_name: str
            Name of the new package.
        :param kwargs:
            workflow_mode: str
                The workflow mode of the package, possible values are "ONLY_ME", "ME_AND_OTHERS" and "ONLY_OTHERS".
                If no workflow_mode is given, the default is used as per the settings in your SigningHub enterprise.
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/packages"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'package_name': package_name
        }
        if "workflow_mode" in kwargs:
            data["workflow_mode"] = kwargs["workflow_mode"]
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def rename_package(self, package_id: int, new_name: str) -> requests.models.Response:
        """ Rename a specific package.

        :param package_id: int
            ID of the package to be renamed.
        :param new_name: str
            New name of the package.
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'package_name': new_name
        })
        return requests.put(url=url, headers=headers, data=data)

    def upload_document(self, package_id: int, path_to_files_folder: str, file_name: str, x_source="API", **kwargs) \
            -> requests.models.Response:
        """ Uploading a document to a specific package.

        :param package_id: int
            ID of the package to which the document needs to be added.
        :param path_to_files_folder: str
            Absolute path of the file that needs to be uploaded.
        :param file_name: str
            Name of the file.
        :param x_source: str
            This is the identification of the source of the document from where the document is uploaded, e.g. "My App".
        :return: response object
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
            'x-file-name': file_name,
            'x-source': x_source,
        }
        if 'x-convert-document' in kwargs:
            headers['x-convert-document'] = kwargs['x-convert-document']
        data = open(path_to_files_folder + file_name, "rb").read()
        return requests.post(url=url, headers=headers, data=data)

    def apply_workflow_template(self, package_id: int, document_id: int, template_name: str, **kwargs) \
            -> requests.models.Response:
        """ Applying a template on a document within a package.

        :param package_id: int
            ID of the package the template should be applied to.
        :param document_id: int
            ID of the document within the package the template should be applied to.
        :param template_name: str
            Name of the template to be applied.
        :param kwargs:
            apply_to_all: bool
                True if the template is to be applied on all documents within the package.
                False if not.
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/template"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            "template_name": template_name
        }
        if "apply_to_all" in kwargs:
            data["apply_to_all"] = kwargs["apply_to_all"]
        data = json.dumps(data)
        return requests.post(url=url, data=data, headers=headers)

    def share_document_package(self, package_id: int) -> requests.models.Response:
        """ Share a specific package.

        :param package_id: int
            ID of the package to be shared.
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.post(url=url, headers=headers)

    def change_document_package_owner(self, package_id: int, new_owner: str) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/owner"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'owner': new_owner
        })
        return requests.put(url=url, headers=headers, data=data)

    def get_document_details(self, package_id: int, document_id: int) -> requests.models.Response:
        """ Get the details of a specific document

        :param package_id: int
            ID of the package.
        :param document_id: int
            ID of the document.
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/details"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
        }
        return requests.get(url=url, headers=headers)

    def get_document_image(self, package_id: int, document_id: int, page_number: int, resolution: str, base_64=False,
                           **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}" \
              f"/images/{page_number}/{resolution}"
        if base_64:
            url += "/base64"
        headers = {
            'Accept': 'image/png',
            'Authorization': 'Bearer ' + self.access_token
        }
        if 'x-password' in kwargs:
            headers['x-password'] = kwargs['x-password']
        if 'x-otp' in kwargs:
            headers['x-otp'] = kwargs['x-otp']
        return requests.get(url=url, headers=headers)

    def download_document(self, package_id: int, document_id: str, base_64=False, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}"
        if base_64:
            url += "/base64"
        headers = {
            'Accept': 'application/octet-stream',
            'Authorization': 'Bearer ' + self.access_token
        }
        if 'x_password' in kwargs:
            headers['x-password'] = kwargs['x_password']
        if "x_otp" in kwargs:
            headers['x-otp'] = kwargs['x_otp']
        return requests.get(url=url, headers=headers)

    def rename_document(self, package_id: int, document_id: int, new_document_name: str) -> requests.models.Response:
        """ Rename a specific document within a package.

        :param package_id: int
            ID of the package in which the document is located.
        :param document_id: int
            ID of the document to be renamed.
        :param new_document_name: str
            New name for the document.
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'document_name': new_document_name
        })
        return requests.put(url=url, headers=headers, data=data)

    def delete_document(self, package_id: int, document_id: int) -> requests.models.Response:
        """ Delete a specific document within a package.

        :param package_id: int
            ID of the package where the document is in.
        :param document_id: int
            ID of the document to be deleted.
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.delete(url=url, headers=headers)

    def get_certify_policy_for_document(self, package_id: int, document_id: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/certify"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def update_certify_policy_for_document(self, package_id: int, document_id: int, enabled: bool, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/certify"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'certify': {
                'enabled': enabled,
            }
        }
        if 'permission' in kwargs:
            data['certify']['permission'] = kwargs['permission']
        if 'lock_form_fields' in kwargs:
            data['lock_form_fields'] = kwargs['lock_form_fields']
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def get_package_verification(self, package_id: int, base_64=True) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/verification"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
            'x-base64': base_64
        }
        return requests.get(url=url, headers=headers)

    def get_document_verification(self, package_id: int, document_id: int, base_64=True) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/verification"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
            'x-base64': base_64
        }
        return requests.get(url=url, headers=headers)

    def change_document_order(self, package_id: int, document_id: int, new_document_order: int) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/reorder"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
        }
        data = json.dumps({
            'order': new_document_order
        })
        return requests.put(url=url, headers=headers, data=data)

    def get_packages(self, document_status: str, page_number: int, records_per_page: int, **kwargs) \
            -> requests.models.Response:
        """ Get all packages of a specific user with a document status filter.

        :param document_status: str
            The status of the packages. Possible values include "ALL", "DRAFT", "PENDING", "SIGNED", "DECLINED",
            "INPROGRESS", "EDITED", "REVIEWED", "COMPLETED".
        :param page_number: int
            Page number of the returned info.
        :param records_per_page: int
            Number of records per page.
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/packages/{document_status}/{page_number}/{records_per_page}"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        if 'x_search_text' in kwargs:
            headers['x-search-text'] = kwargs['x_search_text']
        return requests.get(url=url, headers=headers)

    def delete_package(self, package_id: int) -> requests.models.Response:
        """ Delete a specific package.

        :param package_id: int
            ID of the package to be deleted.
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
        }
        return requests.delete(url=url, headers=headers)

    def download_package(self, package_id: int, base_64=False, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}"
        if base_64:
            url += "/base64"
        headers = {
            'Accept': 'application/octet-stream',
            'Authorization': 'Bearer ' + self.access_token,
        }
        if 'x-password' in kwargs:
            headers['x-password'] = kwargs['x-password']
        if 'x-otp' in kwargs:
            headers['x-otp'] = kwargs['x-otp']
        return requests.get(url=url, headers=headers)

    def open_document_package(self, package_id: int, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.url}/packages/{package_id}/open"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
        }
        if 'x-password' in kwargs:
            headers['x-password'] = kwargs['x-password']
        if 'x-otp' in kwargs:
            headers['x-otp'] = kwargs['x-otp']
        return requests.get(url=url, headers=headers)

    def close_document_package(self, package_id: int) -> requests.models.Response:
        url = f"{self.url}/v{self.url}/packages/{package_id}/close"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
        }
        return requests.get(url=url, headers=headers)

    # Document workflow

    def get_workflow_details(self, package_id: int) -> requests.models.Response:
        """ Get the details of a specific workflow.

        :param package_id: int
            Package ID of the package you want to get details on.
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
        }
        return requests.get(url=url, headers=headers)

    def update_workflow_details(self, package_id: int, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = dict()
        keyworded_arguments = ['workflow_mode', 'workflow_type', 'continue_on_decline', 'message']
        for argument in keyworded_arguments:
            if argument in kwargs:
                data[argument] = kwargs[argument]
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def get_workflow_history(self, package_id: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/log"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def get_workflow_history_details(self, package_id: int, log_id: int, base_64=True) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/log/{log_id}/details"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
            'x-base64': base_64
        }
        return requests.get(url=url, headers=headers)

    def get_certificate_saved_in_workflow_history(self, package_id: int, log_id: int, encryption_key: str) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/log/{log_id}/details/{encryption_key}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def get_process_evidence_report(self, package_id: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/report"
        headers = {
            'Accept': 'application/octet-stream',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def update_post_processing(self, package_id: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/post_process"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def add_users_to_workflow(self, package_id: int, user_email: str, user_name: str, role: str, **kwargs) \
            -> requests.models.Response:
        """ Adding a user to a workflow.

        :param package_id: int
            ID of the package the user should be added to.
        :param user_email: str
            email address of the user whom should be added
        :param user_name: str
            username of the user whom should be added
        :param role: str
            role of the user in the workflow. Possible values include:  "SIGNER", "REVIEWER", "EDITOR",
            "CARBON_COPY" or "INPERSON_HOST"
        :param kwargs:
            email_notifications: (bool)(optional)
                If set to True, SigningHub will send notifications to the user via email as per the document owner
                and user notification settings.
                A value of False means no notifications will be sent to user throughout the workflow.
            signing_order: (int)(optional)
                Order of the recipient in the workflow.
                This signing order is mandatory when workflow type is "CUSTOM".
        :return: response object
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/users"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = [{
            'user_email': user_email,
            'user_name': user_name,
            'role': role,
        }]
        if "email_notifications" in kwargs:
            data[0]["email_notifications"] = kwargs["email_notifications"]
        if "signing_order" in kwargs:
            data[0]["signing_order"] = kwargs["signing_order"]
        data = json.dumps(data)
        return requests.post(url=url, data=data, headers=headers)

    def update_workflow_user(self, package_id: int, order: int, **kwargs) -> requests.models.Response:
        """ Updating a workflow user.

        :param package_id: int
            ID of the package in which the user should be updated.
        :param order: int
            Order of the user in the workflow.
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
            email_notifications: bool
                Setting its value to "true" sends an email notification to the user when its turn arrives in workflow.
                Setting its value to "false" does not send the email notification to the user on its turn.
                If no value is provided, old value will be retained.
            signing_order: int
                Order in which the workflow will be signed by the recipients.
                This signing order is important when workflow type is set to "CUSTOM".
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/{order}/user"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = dict()
        keyworded_arguments = ['user_email', 'user_name', 'role', 'email_notification', 'signing_order']
        for argument in keyworded_arguments:
            if argument in kwargs:
                data[argument] = kwargs[argument]
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def add_groups_to_workflow(self, package_id: int, group_name: str, **kwargs) -> requests.models.Response:
        """ Adding pre-defined groups to a package workflow.

        :param package_id: int
            ID of the package the group should be added to.
        :param group_name: str
            Name of the group that should be added to the workflow.
        :param kwargs:
            role: str
                role of the group as a recipient in the workflow. Possible value are "SIGNER",
                "REVIEWER", "EDITOR","CARBON_COPY" and "INPERSON_HOST".
                However, while XML type document preparation, only supported role types are "SIGNER", "REVIEWER"
                and "CARBON_COPY".
            email_notifications: bool
                Setting its value to "true" sends an email notification to the user when its turn arrives in workflow.
                Setting its value to "false" does not send the email notification to the user on its turn.
                If no value is provided, default value of "true" will be set.
            signing_order: int
                Order in which the workflow will be signed by the recipients.
                This signing order is only important when workflow type is set to "CUSTOM".
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/groups"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'group_name': group_name
        }
        keyworded_arguments = ['role', 'email_notification', 'signing_order']
        for argument in keyworded_arguments:
            if argument in kwargs:
                data[argument] = kwargs[argument]
        payload = list()
        payload.append(data)
        payload = json.dumps(payload)
        return requests.post(url=url, headers=headers, data=payload)

    def update_workflow_group(self, package_id: int, order: int, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/packages/{package_id}/workflow/{order}/group"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = dict()
        keyworded_arguments = ['group_name', 'role', 'email_notification', 'signing_order']
        for argument in keyworded_arguments:
            if argument in kwargs:
                data[argument] = kwargs[argument]
        return requests.put(url=url, headers=headers, data=data)

    def add_placeholder_to_workflow(self, package_id: int, placeholder_name: str, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/placeholder"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = [
            {
                'placeholder': placeholder_name
            }
        ]
        keyworded_arguments = ['role', 'email_notification', 'signing_order']
        for argument in keyworded_arguments:
            if argument in kwargs:
                data[0][argument] = kwargs[argument]
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def update_placeholder(self, package_id: int, order: int, **kwargs) -> requests.models.Response:
        """ Updating a placeholder on a workflow.
        Changeable properties include: placeholder name, role, email notifications, signing order.

        :param package_id: int
            ID of the package in which you want to update the placeholder.
        :param order: int
            The order of the placeholder.
        :param kwargs:
            placeholder: str
                Changing the name of the placeholder.
            role: str
                Changing the role of the placeholder. Options: "SIGNER", "REVIEWER", "EDITOR", "CARBON_COPY" and
                "INPERSON_HOST".
            email_notifications: bool
                Setting its value to "true" sends an email notification to the user when its turn arrives in workflow.
                Setting its value to "false" does not send the email notification to the user on its turn.
                If no value is provided, old value will be retained.
            signing_order: int
                Order in which the workflow will be signed by the recipients.
                The signing order is only important when workflow type is set to "CUSTOM".
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/enterprise/packages/{package_id}/workflow/{order}/placeholder"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = dict()
        keyworded_arguments = ['placeholder', 'role', 'email_notification', 'signing_order']
        for argument in keyworded_arguments:
            if argument in kwargs:
                data[argument] = kwargs[argument]
        data = json.dumps(data)
        return requests.put(url=url, data=data, headers=headers)

    def get_workflow_users(self, package_id: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/users"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def update_workflow_users_order(self, package_id: int, old_order: int, new_order: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/{old_order}/reorder"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            "order": new_order
        })
        return requests.put(url=url, headers=headers, data=data)

    def get_workflow_user_permissions(self, package_id: int, order: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/{order}/permissions"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def update_workflow_user_permissions(self, package_id: int, order: int, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/{order}/permissions"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'permissions': {
                'legal_notice': dict()
            }
        }
        if 'apply_to_all' in kwargs:
            if type(kwargs['apply_to_all']) is not bool:
                raise raise_valueerror('apply_to_all', type(kwargs['apply_to_all']), type(bool))
            data['apply_to_all'] = kwargs['apply_to_all']
        if 'print' in kwargs:
            if type(kwargs['print']) is not bool:
                raise raise_valueerror('print', type(kwargs['print']), type(bool))
            data['permissions']['print'] = kwargs['print']
        if 'download' in kwargs:
            if type(kwargs['download']) is not bool:
                raise raise_valueerror('download', type(kwargs['download']), type(bool))
            data['permissions']['download'] = kwargs['download']
        if 'add_text' in kwargs:
            if type(kwargs['add_text']) is not bool:
                raise raise_valueerror('add_text', type(kwargs['add_text']), type(bool))
            data['permissions']['add_text'] = kwargs['add_text']
        if 'add_attachment' in kwargs:
            if type(kwargs['add_attachment']) is not bool:
                raise raise_valueerror('add_attachment', type(kwargs['add_attachment']), type(bool))
            data['permissions']['add_attachment'] = kwargs['add_attachment']
        if 'change_recipients' in kwargs:
            if type(kwargs['change_recipients']) is not bool:
                raise raise_valueerror('change_recipients', type(kwargs['change_recipients']), type(bool))
            data['permissions']['change_recipients'] = kwargs['change_recipients']
        if 'legal_notice_enabled' in kwargs:
            if type(kwargs['legal_notice_enabled']) is not bool:
                raise raise_valueerror('legal_notice_enabled', type(kwargs['legal_notice_enabled']), type(bool))
            data['permissions']['legal_notice']['enabled'] = kwargs['legal_notice_enabled']
        if 'legal_notice_name' in kwargs:
            if type(kwargs['legal_notice_name']) is not str:
                raise raise_valueerror('legal_notice_name', type(kwargs['legal_notice_name']), type(str))
            data['permissions']['legal_notice']['legal_notice_name'] = kwargs['legal_notice_name']

        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def get_workflow_user_authentication_document_opening(self, package_id: int, order: int) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/{order}/authentication"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def update_workflow_user_authentication_document_opening(self, package_id: int, order: int, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/{order}/authentication"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'authentication': {
                'password': dict(),
                'sms_otp': dict()
            },
            'access_duration': {
                'duration_by_date': {
                    'duration': dict()
                },
                'duration_by_days': {
                    'duration': dict()
                }
            }
        }
        if 'apply_to_all' in kwargs:
            if type(kwargs['apply_to_all']) is not bool:
                raise raise_valueerror('apply_to_all', type(kwargs['apply_to_all']), type(bool))
            data['apply_to_all'] = kwargs['apply_to_all']
        if 'authentication_enabled' in kwargs:
            if type(kwargs['authentication_enabled']) is not bool:
                raise raise_valueerror('authentication_enabled', type(kwargs['authentication_enabled']), type(bool))
            data['authentication']['enabled'] = kwargs['authentication_enabled']
        if 'authentication_password_enabled' in kwargs:
            if type(kwargs['authentication_password_enabled']) is not bool:
                raise raise_valueerror('authentication_password_enabled',
                                       type(kwargs['authentication_password_enabled']), type(bool))
            data['authentication']['password']['enabled'] = kwargs['authentication_password_enabled']
        if 'user_password' in kwargs:
            if type(kwargs['user_password']) is not str:
                raise raise_valueerror('user_password', type(kwargs['user_password']), type(str))
            data['authentication']['password']['user_password'] = kwargs['user_password']
        if 'sms_otp_enabled' in kwargs:
            if type(kwargs['sms_otp_enabled']) is not bool:
                raise raise_valueerror('sms_otp_enabled', type(kwargs['sms_otp_enabled']), type(bool))
            data['authentication']['sms_otp']['enabled'] = kwargs['sms_otp_enabled']
        if 'mobile_number' in kwargs:
            if type(kwargs['mobile_number']) is not str:
                raise raise_valueerror('mobile_number', type(kwargs['mobile_number']), type(str))
            data['authentication']['sms_otp']['mobile_number'] = kwargs['mobile_number']
        if 'access_duration_enabled' in kwargs:
            if type(kwargs['access_duration_enabled']) is not bool:
                raise raise_valueerror('access_duration_enabled', type(kwargs['access_duration_enabled']), type(bool))
            data['access_duration_enabled']['enabled'] = kwargs['access_duration_enabled']
        if 'access_duration_duration_by_date' in kwargs:
            if type(kwargs['access_duration_duration_by_date']) is not bool:
                raise raise_valueerror('access_duration_duration_by_date',
                                       type(kwargs['access_duration_duration_by_date']), type(bool))
            data['access_duration_enabled']['duration_by_date']['enabled'] = kwargs['access_duration_duration_by_date']
        if 'access_duration_by_date_start_date_time' in kwargs:
            if type(kwargs['access_duration_by_date_start_date_time']) is not str:
                raise raise_valueerror('access_duration_by_date_start_date_time',
                                       type(kwargs['access_duration_by_date_start_date_time']), type(str))
            data['access_duration_enabled']['duration_by_date']['duration']['start_date_time'] = \
                kwargs['access_duration_by_date_start_date_time']
        if 'access_duration_by_date_end_date_time' in kwargs:
            if type(kwargs['access_duration_by_date_end_date_time']) is not str:
                raise raise_valueerror('access_duration_by_date_end_date_time',
                                       type(kwargs['access_duration_by_date_end_date_time']), type(str))
            data['access_duration_enabled']['duration_by_date']['duration']['end_date_time'] = \
                kwargs['access_duration_by_date_end_date_time']
        if 'access_duration_duration_by_days_enabled' in kwargs:
            if type(kwargs['access_duration_duration_by_days_enabled']) is not bool:
                raise raise_valueerror('access_duration_duration_by_days_enabled',
                                       type(kwargs['access_duration_duration_by_days_enabled']), type(bool))
            data['access_duration_enabled']['duration_by_days']['enabled'] = \
                kwargs['access_duration_duration_by_days_enabled']
        if 'access_duration_duration_by_days_total_days' in kwargs:
            if type(kwargs['access_duration_duration_by_days_total_days']) is not str:
                raise raise_valueerror('access_duration_duration_by_days_total_days',
                                       type(kwargs['access_duration_duration_by_days_total_days']), type(str))
            data['access_duration_enabled']['duration_by_days']['duration']['total_days'] = \
                kwargs['access_duration_duration_by_days_total_days']
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def delete_workflow_user(self, package_id: int, order: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/{order}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.delete(url=url, headers=headers)

    def open_document_via_otp(self, package_id: int, order: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/{order}/authentication/otp"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.post(url=url, headers=headers)

    def open_document_via_password(self, package_id: int, order: int, password: str) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/{order}/authentication/password"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'password': password
        })
        return requests.post(url=url, headers=headers, data=data)

    def get_workflow_reminders(self, package_id: int, order: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/{order}/reminders"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def update_workflow_reminders(self, package_id: int, order: int, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/{order}/reminders"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'repeat': dict()
        }
        if 'apply_to_all' in kwargs:
            if type(kwargs['apply_to_all']) is not bool:
                raise raise_valueerror('apply_to_all', type(kwargs['apply_to_all']), type(bool))
            data['apply_to_all'] = kwargs['apply_to_all']
        if 'enabled' in kwargs:
            if type(kwargs['enabled']) is not bool:
                raise raise_valueerror('enabled', type(kwargs['enabled']), type(bool))
            data['enabled'] = kwargs['enabled']
        if 'remind_after' in kwargs:
            if type(kwargs['remind_after']) is not int:
                raise raise_valueerror('remind_after', type(kwargs['remind_after']), type(int))
            data['remind_after'] = kwargs['remind_after']
        if 'repeat_enabled' in kwargs:
            if type(kwargs['repeat_enabled']) is not bool:
                raise raise_valueerror('repeat_enabled', type(kwargs['repeat_enabled']), type(bool))
            data['repeat']['enabled'] = kwargs['repeat_enabled']
        if 'keep_reminding_after' in kwargs:
            if type(kwargs['keep_reminding_after']) is not int:
                raise raise_valueerror('keep_reminding_after', type(kwargs['keep_reminding_after']), type(int))
            data['repeat']['keep_reminding_after'] = kwargs['keep_reminding_after']
        if 'total_reminders' in kwargs:
            if type(kwargs['total_reminders']) is not int:
                raise raise_valueerror('total_reminders', type(kwargs['total_reminders']), type(int))
            data['repeat']['total_reminders'] = kwargs['total_reminders']
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def complete_workflow_in_the_middle(self, package_id: int) -> requests.models.Response:
        """ Set workflow status to COMPLETED when the workflow is not already COMPLETED.

        :param package_id: int
            Package ID of the workflow that needs to be completed.
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/enterprise/packages/{package_id}/complete"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.post(url=url, headers=headers)

    # Document Preparation

    def get_document_fields(self, package_id: int, document_id: int, page_number: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/{page_number}"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def assign_document_field(self, package_id: int, document_id: int, field_name: str, order: int) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/assign"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps([{
            'field_name': field_name,
            'order': order
        }])
        return requests.put(url=url, headers=headers, data=data)

    # This call is meant for API version 3 only. However, this will work on API version > 3 as well.
    def add_digital_signature_field(self, package_id: int, document_id: int, order: int, page_number: int, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/digital_signature"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'order': order,
            'page_no': page_number,
            'dimensions': dict()
        }
        if 'field_name' in kwargs:
            data['field_name'] = kwargs['field_name']
        if 'display' in kwargs:
            data['display'] = kwargs['display']
        if 'x' in kwargs:
            data['dimensions']['x'] = kwargs['x']
        if 'y' in kwargs:
            data['dimensions']['y'] = kwargs['y']
        if 'width' in kwargs:
            data['dimensions']['width'] = kwargs['width']
        if 'height' in kwargs:
            data['dimensions']['height'] = kwargs['height']
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    # This call is meant for API version 3 only. However, this will work on API version 4 as well.
    def add_electronic_signature_field(self, package_id: int, document_id: int, order: int, page_no: int, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}" \
              f"/fields/electronic_signature"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'order': order,
            'page_no': page_no,
            'dimensions': dict(),
            'authentication': {
                'enabled': False,
                'sms_otp': dict()
            },
        }
        if 'field_name' in kwargs:
            data['field_name'] = kwargs['field_name']
        if 'display' in kwargs:
            data['display'] = kwargs['display']
        if 'x' in kwargs:
            data['dimensions']['x'] = kwargs['x']
        if 'y' in kwargs:
            data['dimensions']['y'] = kwargs['y']
        if 'width' in kwargs:
            data['dimensions']['width'] = kwargs['width']
        if 'height' in kwargs:
            data['dimensions']['height'] = kwargs['height']
        if 'authentication_enabled' in kwargs:
            data['authentication']['enabled'] = kwargs['authentication_enabled']
        if 'authentication_sms_otp_enabled' in kwargs:
            data['authentication']['sms_opt']['enabled'] = kwargs['authentication_sms_otp_enabled']
        if 'mobile_number' in kwargs:
            data['authentication']['sms_opt']['mobile_number'] = kwargs['mobile_number']
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    # This call is meant for API version 4 (or higher).
    def add_signature_field(self, package_id: int, document_id: int, order: int, page_no: int, **kwargs) \
            -> requests.models.Response:
        if self.api_version < 4:
            raise ValueError("API version should be 4 or more recent")
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/signature"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'order': order,
            'page_no': page_no,
            'dimensions': dict()
        }
        keyworded_attributes = ['field_name', 'display', 'x', 'y', 'width', 'height', 'level_of_assurance']
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                if attribute in ['x', 'y', 'width', 'height']:
                    data['dimensions'][attribute] = kwargs[attribute]
                else:
                    data[attribute] = kwargs[attribute]
        data = json.dumps(data)
        return requests.post(url=url, data=data, headers=headers)

    def add_in_person_field(self, package_id: int, document_id: int, order: int, page_number: int, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/in_person_signature"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'order': order,
            'page_no': page_number,
            'dimensions': dict()
        }
        keyworded_attributes = ['field_name', 'placeholder', 'display', 'x', 'y', 'width', 'height']
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                if attribute in ['x', 'y', 'width', 'height']:
                    data['dimensions'][attribute] = kwargs[attribute]
                else:
                    data[attribute] = kwargs[attribute]
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def add_initials_field(self, package_id: int, document_id: int, order: int, page_number: int, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/initials"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'order': order,
            'page_no': page_number,
            'dimensions': dict()
        }
        keyworded_attributes = ['field_name', 'x', 'y', 'width', 'height']
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                if attribute in ['x', 'y', 'width', 'height']:
                    data['dimensions'][attribute] = kwargs[attribute]
                else:
                    data[attribute] = kwargs[attribute]
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def add_textbox_field(self, package_id: int, document_id: int, order: int, page_number: int, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/text"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'order': order,
            'page_no': page_number,
            'font': dict(),
            'dimensions': dict()
        }
        if 'field_name' in kwargs:
            data['field_name'] = kwargs['field_name']
        if 'type' in kwargs:
            data['type'] = kwargs['type']
        if 'format' in kwargs:
            data['format'] = kwargs['format']
        if 'placeholder' in kwargs:
            data['placeholder'] = kwargs['placeholder']
        if 'value' in kwargs:
            data['value'] = kwargs['value']
        if 'max_length' in kwargs:
            data['max_length'] = kwargs['max_length']
        if 'multiline' in kwargs:
            data['multiline'] = kwargs['multiline']
        if 'field_type' in kwargs:
            data['field_type'] = kwargs['field_type']
        if 'validation_rule' in kwargs:
            data['validation_rule'] = kwargs['validation_rule']
        if 'font_name' in kwargs:
            data['font']['name'] = kwargs['font_name']
        if 'font_size' in kwargs:
            data['font']['size'] = kwargs['font_size']
        if 'font_embedded_size' in kwargs:
            data['font']['embedded_size'] = kwargs['font_embedded_size']
        if 'x' in kwargs:
            data['dimensions']['x'] = kwargs['x']
        if 'y' in kwargs:
            data['dimensions']['y'] = kwargs['y']
        if 'width' in kwargs:
            data['dimensions']['width'] = kwargs['width']
        if 'height' in kwargs:
            data['dimensions']['height'] = kwargs['height']
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def add_radiobox_field(self, package_id: int, document_id: int, order: int, page_number: int, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/radio"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'order': order,
            'page_no': page_number,
            'dimensions': dict()
        }
        if 'field_name' in kwargs:
            data['field_name'] = kwargs['field_name']
        if 'value' in kwargs:
            data['value'] = kwargs['value']
        if 'validation_rule' in kwargs:
            data['validation_rule'] = kwargs['validation_rule']
        if 'radio_group_name' in kwargs:
            data['radio_group_name'] = kwargs['radio_group_name']
        if 'x' in kwargs:
            data['dimensions']['x'] = kwargs['x']
        if 'y' in kwargs:
            data['dimensions']['y'] = kwargs['y']
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def add_checkbox_field(self, package_id: int, document_id: int, order: int, page_number: int, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/checkbox"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'order': order,
            'page_no': page_number,
            'dimensions': dict()
        }
        if 'field_name' in kwargs:
            data['field_name'] = kwargs['field_name']
        if 'value' in kwargs:
            data['value'] = kwargs['value']
        if 'validation_rule' in kwargs:
            data['validation_rule'] = kwargs['validation_rule']
        if 'x' in kwargs:
            data['dimensions']['x'] = kwargs['x']
        if 'y' in kwargs:
            data['dimensions']['y'] = kwargs['y']
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def autoplace_fields(self, package_id: int, document_id: int, search_text: str, order: int, field_type: str,
                         **kwargs) -> requests.models.Response:
        """ Automatically placing fields to a predefined string in the document.

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
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/autoplace"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'search_text': search_text,
            'order': order,
            'field_type': field_type,
            'dimensions': dict(),
            'font': dict()
        }
        if "placement" in kwargs:
            data["placement"] = kwargs["placement"]
        if 'level_of_assurance' in kwargs:
            if field_type != 'SIGNATURE':
                raise ValueError(f'Level of assurance cannot be given to field type {field_type}')
            if self.api_version < 4:
                raise ValueError(f"Level of assurance is not supported on API version < 4")
            data['level_of_assurance'] = kwargs['level_of_assurance']
        if 'multiline' in kwargs:
            if field_type != 'TEXT':
                raise ValueError(f"Multiline option cannot be given for field type {field_type}")
            data['multiline'] = kwargs['multiline']
        if 'value' in kwargs:
            if field_type not in ['TEXT', 'RadioBox', 'CheckBox']:
                raise ValueError(f'Value cannot be assigned to field type {field_type}')
            data['value'] = kwargs['value']
        if 'max_length' in kwargs:
            if field_type in ['SIGNATURE', 'DIGITAL_SIGNATURE', 'ELECTRONIC_SIGNATURE', 'RadioBox', 'CheckBox']:
                raise ValueError(f"max_length cannot be set for field type {field_type}")
            data['field_type'] = kwargs['field_type']
        if 'validation_rule' in kwargs:
            if field_type not in ['CheckBox', 'RadioBox']:
                raise ValueError(f"validation_rule cannot be set for field type {field_type}")
            data['validation_rule'] = kwargs['validation_rule']
        if 'radio_group_name' in kwargs:
            if field_type != "RadioBox":
                raise ValueError(f"radio_group_name cannot be set for field type {field_type}")
            data['radio_group_name'] = kwargs['radio_group_name']
        if 'placeholder' in kwargs:
            if field_type != "IN_PERSON_SIGNATURE":
                raise ValueError(f"Parameter placeholder cannot be set for field type {field_type}")
            data['field_type'] = kwargs['field_type']
        if 'format' in kwargs:
            if field_type != 'DATE':
                raise ValueError(f"Parameter format cannot be set for field type {field_type}")
            data['placeholder'] = kwargs['placeholder']
        if 'font_name' in kwargs:
            if field_type != 'TEXT':
                raise ValueError(f"Parameter font_name cannot be set for field type {field_type}")
            data['font']['name'] = kwargs['font_name']
        if 'font_size' in kwargs:
            if field_type != 'TEXT':
                raise ValueError(f"Parameter font_size cannot be set for field type {field_type}")
            data['font']['size'] = kwargs['font_size']
        if 'font_embedded_size' in kwargs:
            if field_type != 'TEXT':
                raise ValueError(f"Parameter font_embedded_size cannot be set for field type {field_type}")
            data['font']['embedded_size'] = kwargs['font_embedded_size']
        if "width" in kwargs:
            data["dimensions"]["width"] = kwargs["width"]
        if "height" in kwargs:
            data["dimensions"]["height"] = kwargs["height"]
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def update_digital_signature_field(self, package_id: int, document_id: int, field_name: str, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/digital_signature"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'field_name': field_name,
            'dimensions': dict()
        }
        if 'renamed_as' in kwargs:
            data['renamed_as'] = kwargs['renamed_as']
        if 'page_number' in kwargs:
            data['page_no'] = kwargs['page_number']
        if 'display' in kwargs:
            data['display'] = kwargs['display']
        if 'x' in kwargs:
            data['dimensions']['x'] = kwargs['x']
        if 'y' in kwargs:
            data['dimensions']['y'] = kwargs['y']
        if 'width' in kwargs:
            data['dimensions']['width'] = kwargs['width']
        if 'height' in kwargs:
            data['dimensions']['height'] = kwargs['height']
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def update_electronic_signature_fields(self, package_id: int, document_id: int, field_name: str, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}" \
              f"/fields/electronic_signature"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'field_name': field_name,
            'dimensions': dict(),
            "authentication": {
                "sms_otp": dict()
            },
        }
        if 'renamed_as' in kwargs:
            data['renamed_as'] = kwargs['renamed_as']
        if 'display' in kwargs:
            data['display'] = kwargs['display']
        if 'page_number' in kwargs:
            data['page_no'] = kwargs['page_number']
        if 'x' in kwargs:
            data['dimensions']['x'] = kwargs['x']
        if 'y' in kwargs:
            data['dimensions']['y'] = kwargs['y']
        if 'width' in kwargs:
            data['dimensions']['width'] = kwargs['width']
        if 'height' in kwargs:
            data['dimensions']['height'] = kwargs['height']
        if 'authentication_enabled' in kwargs:
            data['authentication']['enabled'] = kwargs['authentication_enabled']
        if 'authentication_sms_otp_enabled' in kwargs:
            data['authentication']['sms_opt']['enabled'] = kwargs['authentication_sms_otp_enabled']
        if 'mobile_number' in kwargs:
            data['authentication']['sms_opt']['mobile_number'] = kwargs['mobile_number']
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def update_in_person_field(self, package_id: int, document_id: int, field_name: str, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/in_person_signature"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'field_name': field_name,
            'dimensions': dict(),
            'authentication': {
                'sms_otp': dict()
            }
        }
        if 'renamed_as' in kwargs:
            data['renamed_as'] = kwargs['renamed_as']
        if 'page_number' in kwargs:
            data['page_no'] = kwargs['page_number']
        if 'placeholder' in kwargs:
            data['placeholder'] = kwargs['placeholder']
        if 'display' in kwargs:
            data['display'] = kwargs['display']
        if 'x' in kwargs:
            data['dimensions']['x'] = kwargs['x']
        if 'y' in kwargs:
            data['dimensions']['y'] = kwargs['y']
        if 'width' in kwargs:
            data['dimensions']['width'] = kwargs['width']
        if 'height' in kwargs:
            data['dimensions']['height'] = kwargs['height']
        if 'authentication_enabled' in kwargs:
            data['authentication']['enabled'] = kwargs['authentication_enabled']
        if 'authentication_sms_otp_enabled' in kwargs:
            data['authentication']['sms_opt']['enabled'] = kwargs['authentication_sms_otp_enabled']
        if 'mobile_number' in kwargs:
            data['authentication']['sms_opt']['mobile_number'] = kwargs['mobile_number']
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def update_initials_field(self, package_id: int, document_id: int, field_name: str, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/initials"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'field_name': field_name,
            'dimensions': dict()
        }
        if 'renamed_as' in kwargs:
            data['renamed_as'] = kwargs['renamed_as']
        if 'page_number' in kwargs:
            data['page_no'] = kwargs['page_number']
        if 'x' in kwargs:
            data['dimensions']['x'] = kwargs['x']
        if 'y' in kwargs:
            data['dimensions']['y'] = kwargs['y']
        if 'width' in kwargs:
            data['dimensions']['width'] = kwargs['width']
        if 'height' in kwargs:
            data['dimensions']['height'] = kwargs['height']
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def update_textbox_field(self, package_id: int, document_id: int, field_name: str, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/text"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'field_name': field_name,
            'font': dict(),
            'dimensions': dict()
        }
        keyworded_attributes = ['renamed_as', 'page_number', 'page_number', 'type', 'format', 'placeholder', 'value',
                                'max_length', 'multiline', 'field_type', 'validation_rule', 'font_name', 'font_size',
                                'font_embedded_size', 'x', 'y', 'width', 'height']
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                if 'font' in attribute:
                    data['font'][attribute[5:]] = kwargs[attribute]
                elif attribute in ['x', 'y', 'width', 'height']:
                    data['dimensions'][attribute] = kwargs[attribute]
                else:
                    data[attribute] = kwargs[attribute]
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def update_radiobox_field(self, package_id: int, document_id: int, field_name: str, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/radio"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'field_name': field_name,
            'dimensions': dict()
        }
        if 'renamed_as' in kwargs:
            data['renamed_as'] = kwargs['renamed_as']
        if 'page_number' in kwargs:
            data['page_no'] = kwargs['page_number']
        if 'value' in kwargs:
            data['value'] = kwargs['value']
        if 'validation_rule' in kwargs:
            data['validation_rule'] = kwargs['validation_rule']
        if 'radio_group_name' in kwargs:
            data['radio_group_name'] = kwargs['radio_group_name']
        if 'x' in kwargs:
            data['dimensions']['x'] = kwargs['x']
        if 'y' in kwargs:
            data['dimensions']['y'] = kwargs['y']
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def update_checkbox_field(self, package_id: int, document_id: int, field_name: str, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/checkbox"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'field_name': field_name,
            'dimensions': dict()
        }
        if 'renamed_as' in kwargs:
            data['renamed_as'] = kwargs['renamed_as']
        if 'page_number' in kwargs:
            data['page_no'] = kwargs['page_number']
        if 'value' in kwargs:
            data['value'] = kwargs['value']
        if 'validation_rule' in kwargs:
            data['validation_rule'] = kwargs['validation_rule']
        if 'x' in kwargs:
            data['dimensions']['x'] = kwargs['x']
        if 'y' in kwargs:
            data['dimensions']['y'] = kwargs['y']
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def delete_document_field(self, package_id: int, document_id: int, field_name: str) -> requests.models.Response:
        """ Deleting a field from a document.

        :param package_id: int
            ID of the package.
        :param document_id: int
            ID of the document where the field is placed.
        :param field_name: str
            Name of the field which will be deleted.
        :return: requests.models.Response
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'field_name': field_name
        })
        return requests.delete(url=url, data=data, headers=headers)

    def signer_authentication_via_otp(self, package_id: int, document_id: int, field_name: str) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/otp"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'field_name': field_name
        })
        return requests.post(url=url, headers=headers, data=data)

    def fill_initials(self, package_id: int, document_id: int, field_name: str, base64_image: bytes, **kwargs) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/otp"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'field_name': field_name,
            'image': base64_image
        }
        if 'apply_to_all' in kwargs:
            data['apply_to_all'] = kwargs['apply_to_all']
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def fill_form_fields(self, package_id: int, document_id: int, field_type: str, field_name: str, field_value,
                         radio_group_name=None, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'text': list(),
            'radio': list(),
            'checkbox': list(),
            'dropdown': list(),
            'listbox': list()
        }
        if 'auto_save' in kwargs:
            data['auto_save'] = kwargs['auto_save']
        if field_type in ['text', 'radio', 'checkbox', 'dropdown', 'listbox']:
            field_data = {
                'field_name': field_name,
                'value': field_value
            }
            if field_type == 'radio':
                if not radio_group_name:
                    raise ValueError(f"Parameter 'radio_group_name' cannot be None when field type is set to "
                                     f"'{field_type}'")
                field_data['radio_group_name'] = radio_group_name
            data[field_type].append(field_data)
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    # For API v4 and higher only.
    def sign_document_v4(self, package_id: int, document_id: int, field_name: str, hand_signature_image: str,
                         signing_server: str, signing_capacity: str, **kwargs) -> requests.models.Response:
        """ Sign a signature field. This function is for API version 4 (SigningHub version 7.7.9 and above).

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
        :return:
        """
        if self.api_version < 4:
            raise ValueError(f"API version is set to {self.api_version}."
                             f" This call can only be used for API version >= 4.")
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/sign"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'field_name': field_name,
            'hand_signature_image': hand_signature_image,
            'signing_server': signing_server,
            'signing_capacity': signing_capacity
        }

        keyworded_attributes = ['signing_reason', 'signing_location', 'contact_information', 'user_name',
                                'user_password', 'appearance_design', 'skip_verification']
        if 'x_otp' in kwargs:
            headers["x-otp"] = kwargs["x_otp"]
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                data[attribute] = kwargs[attribute]
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def sign_document_v3(self, package_id: int, document_id: int, field_name: str, hand_signature_image: str, **kwargs) \
            -> requests.models.Response:
        """ Sign a signature field. This function is for API version 3 (SigningHub version 7.7.9 and below).

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
        :return:
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/sign"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'field_name': field_name,
            'hand_signature_image': hand_signature_image
        }
        keyworded_attributes = ['signing_reason', 'signing_location', 'contact_information', 'user_name',
                                'user_password', 'appearance_design', 'signing_capacity', 'witness_signing_capacity',
                                'skip_verification']
        if 'x_otp' in kwargs:
            headers["x-otp"] = kwargs["x_otp"]
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                data[attribute] = kwargs[attribute]
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def decline_document(self, package_id: int, **kwargs) -> requests.models.Response:
        """ Decline a pending package through the API

        :param package_id: ID of the package
        :type package_id: int
        :param kwargs:
            reason: Reason for the decline of the package
        :return:
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/decline"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = dict()
        if 'reason' in kwargs:
            data['reason'] = kwargs['reason']
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def approve_document(self, package_id: int, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/approve"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = dict()
        if 'reason' in kwargs:
            data['reason'] = kwargs['reason']
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def submit_document(self, package_id: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/submit"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.post(url=url, headers=headers)

    def recall_document(self, package_id: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.delete(url=url, headers=headers)

    def finish_processing(self, package_id: int) -> requests.models.Response:
        """ Within native SigningHub mobile apps and mobile web use cases,
        this call is necessary to ensure that each user completes their respective actions with respect to SigningHub.

        For example, after a signatory has signed a document in SigningHub App,
        this method is invoked by the application to ensure the workflow continues to process
        and the next signatory is notified, and the document status is available via the configured call-back URL.

        :param package_id: ID of the package that needs to be finished
        :type package_id: int
        :return: response object
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/finish"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.post(url=url, headers=headers)

    def get_registered_devices(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/authorization/devices"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def authorization_signing_request_status(self, package_id: int, document_id: int, field_name: str) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/field/status"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'field_name': field_name
        })
        return requests.post(url=url, headers=headers, data=data)

    # Account Management

    def register_user_free_trial(self, user_email: str, user_name: str, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'user_email': user_email,
            'user_name': user_name,
            'invitation': dict()
        }
        keyworded_attributes = ['job_title', 'company_name', 'mobile_number', 'country', 'time_zone', 'language',
                                'service_agreements', 'marketing_emails']
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                data[attribute] = kwargs[attribute]
        if 'invitation_to_enterprise_name' in kwargs:
            data['invitation']['enterprise_name'] = data['invitation_to_enterprise_name']
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def get_account(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def get_account_password_policy(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account/password_policy"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.post(url=url, headers=headers)

    def get_user_role(self, base64=True) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account/role"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
            'x-base64': base64
        }
        return requests.get(url=url, headers=headers)

    def resend_activation_email(self, user_email: str) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account/activation/resend"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'user_email': user_email
        })
        return requests.post(url=url, headers=headers, data=data)

    def send_forgot_password_request(self, user_email: str) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account/password/reset"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'user_email': user_email
        })
        return requests.post(url=url, headers=headers, data=data)

    def set_new_password(self, new_password: str, security_question: str, security_answer: str) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account/password/new"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.x_change_password_token
        }
        data = json.dumps({
            'password': new_password,
            'security_question': security_question,
            'security_answer': security_answer
        })
        return requests.put(url=url, headers=headers, data=data)

    def get_account_invitations(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account/invitations"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.post(url=url, headers=headers)

    def accept_account_invitations(self, enterprise_name: str) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account/invitations"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'enterprise_name': enterprise_name
        })
        return requests.put(url=url, headers=headers, data=data)

    def reject_all_account_invitations(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account/invitations"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.delete(url=url, headers=headers)

    def account_usage_statistics(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account/statistics/usage"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def document_statistics(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account/statistics/documents"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def get_notifications(self, records_per_page: int, page_number: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account/notifications/{records_per_page}/{page_number}"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def device_registration_for_push_notification(self, device_token: str, os_type: str) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/users/notifications/devices"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'device_token': device_token,
            'os_type': os_type
        })
        return requests.post(url=url, headers=headers, data=data)

    def get_user_activity_logs(self, records_per_page: int, page_number: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account/log/{page_number}/{records_per_page}"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def get_user_activity_logs_details(self, log_id: int, base64=True) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account/log/{log_id}/details"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
            'x-base64': base64
        }
        return requests.get(url=url, headers=headers)

    def add_identity_for_a_user(self, user_email: str, provider: str, name: str, key: str, value: str) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/account/identity"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'user_email': user_email,
            'provider': provider,
            'name': name,
            'key': key,
            'value': value
        })
        return requests.post(url=url, headers=headers, data=data)

    # Personal Settings

    def get_general_profile_information(self):
        url = f"{self.url}/v{self.api_version}/settings/profile"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def update_general_profile_information(self, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/profile/general"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = dict()
        keyworded_attributes = ['user_name', 'job_title', 'company_name', 'mobile_number', 'country', 'time_zone',
                                'language', 'user_national_id']
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                data[attribute] = kwargs[attribute]
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def change_password(self, old_password: str, new_password: str) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/profile/password"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'user_old_password': old_password,
            'user_new_password': new_password
        })
        return requests.put(url=url, headers=headers, data=data)

    def get_profile_picture(self, base64=True) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/profile/general/photo"
        if base64:
            url += "/base64"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def update_profile_picture(self, profile_picture: bytes) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/profile/general/photo/base64"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'photo': profile_picture
        })
        return requests.put(url=url, headers=headers, data=data)

    def update_security_settings(self, password: str, security_question: str, security_answer: str) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/profile/security"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'password': password,
            'question': security_question,
            'answer': security_answer
        })
        return requests.put(url=url, headers=headers, data=data)

    def update_locale_settings(self, country: str, timezone: str, language: str) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/profile/locale"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'country': country,
            'timezone': timezone,
            'language': language
        })
        return requests.put(url=url, headers=headers, data=data)

    def get_signature_settings(self, base64=True) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/signatures"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
            'x-base64': base64
        }
        return requests.get(url=url, headers=headers)

    def get_signature_appearance(self, signature_type: str) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/signatures/appearance/design/{signature_type}/preview"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def get_hand_signature_text_for_web(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/signatures/appearance/hand_signature/web/text"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def get_hand_signature_text_for_mobile(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/signatures/appearance/hand_signature/mobile/text"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def get_hand_signature_upload_for_web(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/signatures/appearance/hand_signature/web/upload"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def get_hand_signature_upload_for_mobile(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/signatures/appearance/hand_signature/mobile/upload"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def update_signature_appearance_design(self, default_design: str) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/signatures/appearance/design"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'default_design': default_design
        })
        return requests.put(url=url, headers=headers, data=data)

    def update_signature_settings_metadata(self, signing_reason: str, signing_location: str, contact_information: str) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/signatures/metadata"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'signing_reason': signing_reason,
            'signing_location': signing_location,
            'contact_information': contact_information
        })
        return requests.put(url=url, headers=headers, data=data)

    def update_hand_signature_browser(self, default_method: str, upload_image: bytes, text_value: str) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/signatures/appearance/browser"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'default_method': default_method,
            'upload_image': upload_image,
            'text_value': text_value
        })
        return requests.put(url=url, headers=headers, data=data)

    def update_hand_signature_mobile(self, default_method: str, upload_image: bytes, text_value: str) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/signatures/appearance/mobile"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'default_method': default_method,
            'upload_image': upload_image,
            'text_value': text_value
        })
        return requests.put(url=url, headers=headers, data=data)

    def get_initials_for_upload_option(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/signatures/appearance/initials/upload"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def get_initials_for_text_option(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/signatures/appearance/initials/text"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def update_initial_appearance(self, default_method: str, upload_image: bytes, text_value: str) \
            -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/signatures/appearance/initials"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'default_method': default_method,
            'upload_image': upload_image,
            'text_value': text_value
        })
        return requests.put(url=url, headers=headers, data=data)

    def get_signature_delegation_settings(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/delegate"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def update_signature_delegation_settings(self, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/delegate"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'delegate': dict()
        }
        if 'enabled' in kwargs:
            data['enabled'] = kwargs['enabled']
        keyworded_attributes = ['user_name', 'user_email', 'from', 'to']
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                data['delegate'][attribute] = kwargs[attribute]
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def add_contact(self, user_email: str, user_name: str) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/contacts"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'user_email': user_email,
            'user_name': user_name
        })
        return requests.post(url=url, headers=headers, data=data)

    def get_contacts(self, records_per_page: int, page_number: int, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/contacts/{records_per_page}/{page_number}"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        keyworded_attributes = ['x-search-text', 'x-enterprise']
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                headers[attribute] = kwargs[attribute]
        return requests.get(url=url, headers=headers)

    def get_groups(self, records_per_page: int, page_number: int, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/groups/{records_per_page}/{page_number}"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        keyworded_attributes = ['x-search-text', 'x-enterprise']
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                headers[attribute] = kwargs[attribute]
        return requests.get(url=url, headers=headers)

    def get_library_documents(self, records_per_page: int, page_number: int, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/library/{records_per_page}/{page_number}"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        keyworded_attributes = ['x-search-text', 'x-enterprise']
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                headers[attribute] = kwargs[attribute]
        return requests.get(url=url, headers=headers)

    def get_templates(self, records_per_page: int, page_number: int, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/templates/{records_per_page}/{page_number}"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        keyworded_attributes = ['x-search-text', 'x-enterprise']
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                headers[attribute] = kwargs[attribute]
        return requests.get(url=url, headers=headers)

    def reset_email_notifications(self) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/notifications/email/reset"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.put(url=url, headers=headers)

    def get_personal_group(self, group_id: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/groups/{group_id}"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def add_personal_group(self, group_name: str, members: list, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/groups"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'Name': group_name,
            'Members': members
        }
        if 'description' in kwargs:
            data['Description'] = kwargs['description']
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def update_personal_group(self, group_id: int, **kwargs) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/groups/{group_id}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = dict()
        keyworded_attributes = ['name', 'description', 'members']
        for attribute in keyworded_attributes:
            if attribute in kwargs:
                data[attribute] = kwargs[attribute]
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def delete_personal_group(self, group_id: int) -> requests.models.Response:
        url = f"{self.url}/v{self.api_version}/settings/groups/{group_id}"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.delete(url=url, headers=headers)


def raise_valueerror(keyword: str, received_type: type, expected_type: type):
    return ValueError(f"Keyword '{keyword}' should be {expected_type} but instead type {received_type} was received")
