import requests
import json


class Connection:
    def __init__(self, url: str, client_id: str, client_secret: str, username=None, password=None, api_port=None,
                 scope=None, api_version=3, access_token=None, refresh_token=None):
        """ Initialize a connection between python and the SigningHub API.

        What needs to be defined:
        - URL
        - Client ID
        - Client secret

        This can be combined with either:
        - An valid access token;
        - A combination of username and password;
        - A refresh token.

        To test your defined URL, you can try an "about" call (which gets SigningHub instance information, no login required).

        :param client_id: str; The client id of the integration in your SigningHub
        :param client_secret: str; The client secret of the integration of your SigningHub
        :param username: str; The username of the user you want to authenticate with
        :param password: str; The password of the given user
        :param url: str; The API URL of the SigningHub instance
        :param api_port: str/int; The port of the API instance. Default value: None
        :param scope: str; The user email address we wish to scope with. Default value: None
        :param api_version: int; The version of the API of SigningHub. SigningHub version <=7.7.9: api_version=3, SigningHub version >=7.7.9: api_version=4
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
    def authenticate(self):
        """ Authentication with username and password.

        When a status code 200 is received, an access_token parameter (str) will be created on the Connection object with the value of the access_token parameter in the returned json.
        If another status code than 200 is received, an access_token parameter will be created on the Connection object with value None.

        :return: response object
        """
        if not self.url or not self.client_id or not self.client_secret:
            raise ValueError("URL, client ID or client secret cannot be None")
        url = "{}/authenticate".format(self.url)
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
        authentication_text = json.loads(authentication_call.text)
        try:
            self.access_token = authentication_text['access_token']
            self.refresh_token = authentication_text['refresh_token']
        except:
            self.access_token = None
        finally:
            return authentication_call

    def authenticate_with_refresh_token(self) -> requests.Response:
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
        response_json = json.loads(r.text)
        try:
            self.access_token = response_json['access_token']
            self.refresh_token = response_json['refresh_token']
        except:
            self.access_token = None
        finally:
            return r

    def get_service_agreements(self):
        url = "{}/v{}/terms".format(self.url, self.api_version)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        return requests.get(url=url, headers=headers)

    def otp_login_authentication(self, mobile_number: str):
        url = "{}/v{}/authentication/otp".format(self.url, self.api_version)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'mobile_number': mobile_number
        }
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    # Enterprise Management

    def about_signinghub(self):
        """ Get information about the SigningHub enterprise this call is executed to.

        :return: JSON response with SigningHub information
        """
        url = "{}/v{}/about".format(self.url, self._api_version)
        headers = {
            'Accept': 'application/json'
        }
        return requests.get(url=url, headers=headers)

    def reset_email_notifications(self):
        url = f"{self.url}/v{self.api_version}/enterprise/notifications/email/reset"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.put(url=url, headers=headers)

    def register_enterprise_user(self, user_email: str, user_name: str, **kwargs):
        url = "{}/v{}/enterprise/users".format(self.url, self.api_version)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'user_email': user_email,
            'user_name': user_name
        }
        if 'job_title' in kwargs:
            data['job_title'] = kwargs['job_title']
        if 'company_name' in kwargs:
            data['company_name'] = kwargs['company_name']
        if 'mobile_number' in kwargs:
            data['mobile_number'] = kwargs['mobile_number']
        if 'user_password' in kwargs:
            data['user_password'] = kwargs['user_password']
        if 'security_question' in kwargs:
            data['security_question'] = kwargs['security_question']
        if 'security_answer' in kwargs:
            data['security_answer'] = kwargs['security_answer']
        if 'enterprise_role' in kwargs:
            data['enterprise_role'] = kwargs['enterprise_role']
        if 'email_notification' in kwargs:
            data['email_notification'] = kwargs['email_notification']
        if 'country' in kwargs:
            data['country'] = kwargs['country']
        if 'time_zone' in kwargs:
            data['time_zone'] = kwargs['time_zone']
        if 'language' in kwargs:
            data['language'] = kwargs['language']
        if 'user_ra_id' in kwargs:
            data['user_ra_id'] = kwargs['user_ra_id']
        if 'user_csp_id' in kwargs:
            data['user_csp_id'] = kwargs['user_csp_id']
        if 'certificate_alias' in kwargs:
            data['certificate_alias'] = kwargs['certificate_alias']
        if 'common_name' in kwargs:
            data['common_name'] = kwargs['common_name']
        data = json.dumps(data)
        return requests.post(url=url, data=data, headers=headers)

    def get_enterprise_users(self, search_string=None):
        url = "{}/v{}/enterprise/users".format(self.url, self.api_version)
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        if search_string:
            headers['Accept'] = search_string
        return requests.get(url=url, headers=headers)

    def update_enterprise_user(self, user_email: str, **kwargs) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/users"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            "user_email": user_email
        }
        if 'user_name' in kwargs:
            data['user_name'] = kwargs['user_name']
        if 'job_title' in kwargs:
            data['job_title'] = kwargs['job_title']
        if 'company_name' in kwargs:
            data['company_name'] = kwargs['company_name']
        if 'mobile_number' in kwargs:
            data['mobile_number'] = kwargs['mobile_number']
        if 'user_password' in kwargs:
            data['user_password'] = kwargs['user_password']
        if 'security_question' in kwargs:
            data['security_question'] = kwargs['security_question']
        if 'security_answer' in kwargs:
            data['security_answer'] = kwargs['security_answer']
        if 'enterprise_role' in kwargs:
            data['enterprise_role'] = kwargs['enterprise_role']
        if 'enabled' in kwargs:
            data['enabled'] = kwargs['enabled']
        if 'country' in kwargs:
            data['country'] = kwargs['country']
        if 'time_zone' in kwargs:
            data['time_zone'] = kwargs['time_zone']
        if 'language' in kwargs:
            data['language'] = kwargs['language']
        if 'user_ra_id' in kwargs:
            data['user_ra_id'] = kwargs['user_ra_id']
        if 'user_csp_id' in kwargs:
            data['user_csp_id'] = kwargs['user_csp_id']
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def delete_enterprise_user(self, user_email: str) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/users"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({'user_email': user_email})
        return requests.delete(url=url, headers=headers, data=data)

    def invite_enterprise_user(self, user_email: str, user_name: str, **kwargs) -> requests.Response:
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
        requests.post(url=url, headers=headers, data=data)

    def get_enterprise_invitations(self, page_number: int, records_per_page: int) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/invitations/{page_number}/{records_per_page}"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def delete_enterprise_user_invitation(self, user_email: str) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/invitations"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({'user_email': user_email})
        return requests.delete(url=url, headers=headers, data=data)

    def get_enterprise_branding(self):
        url = f"{self.url}/v{self.api_version}/enterprise/branding"
        headers = {
            'Accept': 'application/json',
            'x-base64': True,
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def get_package(self, package_id: int) -> requests.Response:
        """ Returns the info of a specific package.

        :param package_id: the package ID of the package
        :return: returns a response object with a json body with parameters:
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

    def get_workflow_users(self, package_id: int) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/packages/{package_id}/workflow/users"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def update_workflow_user(self, package_id: int, order: int, **kwargs) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/packages/{package_id}/workflow/{order}/user"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = dict()
        if 'user_email' in kwargs:
            data['user_email'] = kwargs['user_email']
        if 'user_name' in kwargs:
            data['user_name'] = kwargs['user_name']
        if 'role' in kwargs:
            data['role'] = kwargs['role']
        if 'email_notification' in kwargs:
            data['email_notification'] = kwargs['email_notification']
        if 'signing_order' in kwargs:
            data['signing_order'] = kwargs['signing_order']
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def update_workflow_group(self, package_id: int, order: int, **kwargs) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/packages/{package_id}/workflow/{order}/group"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = dict()
        if 'group_name' in kwargs:
            data['group_name'] = kwargs['group_name']
        if 'role' in kwargs:
            data['role'] = kwargs['role']
        if 'email_notification' in kwargs:
            data['email_notification'] = kwargs['email_notification']
        if 'signing_order' in kwargs:
            data['signing_order'] = kwargs['signing_order']
        return requests.put(url=url, headers=headers, data=data)

    def update_placeholder(self, package_id: int, order: int, **kwargs) -> requests.Response:
        """ Updating a placeholder on a workflow. Changeable properties include: placeholder name, role, email notifications, signing order.

        :param package_id: package ID of the package in which you want to update the placeholder
        :param order: the order of the placeholder
        :param kwargs:
            placeholder (optional)(str): changing the name of the placeholder;
            role (optional)(str): changing the role of the placeholder. Options: "SIGNER", "REVIEWER", "EDITOR","CARBON_COPY" and "INPERSON_HOST";
            email_notifications (optional)(boolean): Setting its value to "true" sends an email notification to the user when its turn arrives in workflow. Setting its value to "false" does not send the email notification to the user on its turn. If no value is provided, old value will be retained;
            signing_order (optional)(int):  Order in which the workflow will be signed by the recipients. This signing order is important when workflow type is set to "CUSTOM".
        :return: returns a response object with empty body on success.
        """
        url = f"{self.url}/v{self.api_version}/enterprise/packages/{package_id}/workflow/{order}/placeholder"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = dict()
        if "placeholder" in kwargs:
            data["placeholder"] = kwargs["placeholder"]
        if "role" in kwargs:
            data["role"] = kwargs["role"]
        if "email_notifications" in kwargs:
            data["email_notifications"] = kwargs["email_notifications"]
        if "signing_order" in kwargs:
            data["signing_order"] = kwargs["signing_order"]
        data = json.dumps(data)
        return requests.put(url=url, data=data, headers=headers)

    def complete_workflow_in_the_middle(self, package_id: int) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/packages/{package_id}/complete"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.post(url=url, headers=headers)

    def add_certificate(self, user_email: str, capacity_name: str, certificate_alies: str, level_of_assurance: str,
                        key_protection_option: str, is_default: bool) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/signingcertificates"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'user_email': user_email,
            'capacity_name': capacity_name,
            'certificate_alias': certificate_alies,
            'level_of_assurance': level_of_assurance,
            'key_protection_option': key_protection_option,
            "isDefault": is_default
        }
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def delete_certificate(self, certificate_id: int, user_email: str) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/signingcertificate/{certificate_id}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = json.dumps({
            'user_email': user_email
        })
        requests.delete(url=url, headers=headers, data=data)

    def get_enterprise_group(self, group_id: int):
        url = f"{self.url}/v{self.api_version}/enterprise/groups/{group_id}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def add_enterprise_group(self, group_name: str, members: list, **kwargs) -> requests.Response:
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

    def update_enterprise_group(self, group_id: int, **kwargs) -> requests.Response:
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

    def delete_enterprise_group(self, group_id: int) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/enterprise/groups/{group_id}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.delete(url=url, headers=headers)

    # Document Package

    def add_package(self, package_name, **kwargs):
        """ Create a new package in SigningHub.

        :param package_name: Name of the package
        :param kwargs:
            workflow_mode (optional)(str): The workflow mode of the package, possible values are "ONLY_ME", "ME_AND_OTHERS" and "ONLY_OTHERS". If no workflow_mode is given, the default is used as per the settings in your SigningHub enterprise
        :return: response object
        """
        url = self.url + "/v3/packages"
        headers = {
            "Authorization": "Bearer " + self.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        data = {
            "package_name": package_name
        }
        if "workflow_mode" in kwargs:
            data["workflow_mode"] = kwargs["workflow_mode"]
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def rename_package(self, package_id: int, new_name: str) -> requests.Response:
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

    def upload_document(self, package_id: int, path_to_files_folder: str, file_name, **kwargs):
        """ Uploading a document to a specific package.

        :param package_id: int; Package ID of the package where the document needs to be added.
        :param path_to_files_folder: str; Absolute path of the file that needs to be uploaded.
        :param file_name: str; Name of the file.
        :return: response object
        """
        url = self.url + "/v3/packages/" + str(package_id) + "/documents"
        headers = {
            "Authorization": "Bearer " + self.access_token,
            'Content-Type': 'application/octet-stream',
            'Accept': 'application/json',
            'x-file-name': file_name,
            'x-source': 'API',
        }
        if 'x-convert-document' in kwargs:
            headers['x-convert-document'] = kwargs['x-convert-document']
        data = open(path_to_files_folder + file_name, "rb").read()
        return requests.post(url=url, headers=headers, data=data)

    def apply_workflow_template(self, package_id: int, document_id: int, template_name: str, **kwargs):
        """ Applying a template on a document within a package.

        :param package_id: int; ID of the package the template should be applied to.
        :param document_id: int; ID of the document within the package the template should be applied to.
        :param template_name: str; Name of the template to be applied.
        :param kwargs:
            apply_to_all: (bool)(optional); True, if template is to be applied on all the documents in the package. False if not.
        :return: response object
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/template"
        headers = {
            "Authorization": "Bearer " + self.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        data = {
            "template_name": template_name
        }
        if "apply_to_all" in kwargs:
            data["apply_to_all"] = kwargs["apply_to_all"]
        data = json.dumps(data)
        return requests.post(url=url, data=data, headers=headers)

    def share_document_package(self, package_id: int):
        """ Share a package.

        :param package_id: int; ID of the package to be shared.
        :return: response object
        """
        url = "{}/v{}/packages/{}/workflow".format(self.url, self.api_version, package_id)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.post(url=url, headers=headers)

    def change_document_package_owner(self, package_id: int, new_owner: str) -> requests.Response:
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

    def get_document_details(self, package_id: int, document_id: int) -> requests.Response:
        """ Get the details of a specific document

        :param package_id: int; ID of the package
        :param document_id: int; ID of the document
        :return: response object
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/details"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
        }
        return requests.get(url=url, headers=headers)

    def get_document_image(self, package_id: int, document_id: int,
                           page_number: int, resolution: str, base_64=False, **kwargs) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/images/{page_number}/{resolution}"
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

    def download_document(self, package_id: int, document_id: str, base_64=False, **kwargs) -> requests.Response:
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

    def rename_document(self, package_id: int, document_id: int, new_document_name: str) -> requests.Response:
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

    def delete_document(self, package_id: int, document_id: int) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.delete(url=url, headers=headers)

    def get_certify_policy_for_document(self, package_id: int, document_id: int) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/certify"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def update_certify_policy_for_document(self, package_id: int, document_id: int,
                                           enabled: bool, **kwargs) -> requests.Response:
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

    def get_package_verification(self, package_id: int, base_64=True) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/verification"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
            'x-base64': base_64
        }
        return requests.get(url=url, headers=headers)

    def get_document_verification(self, package_id: int, document_id: int, base_64=True) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/verification"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
            'x-base64': base_64
        }
        return requests.get(url=url, headers=headers)

    def change_document_order(self, package_id: int, document_id: int, new_document_order: int) -> requests.Response:
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

    def get_packages(self, document_status: str, page_no: int, records_per_page: int, **kwargs):
        """ Get all packages of a specific user with a document status filter.

        :param document_status: str; The status of the packages. Possible values include "ALL", "DRAFT", "PENDING", "SIGNED", "DECLINED", "INPROGRESS", "EDITED", "REVIEWED", "COMPLETED".
        :param page_no: int; Page number of the returned info.
        :param records_per_page: int; Number of records per page.
        :return: response object
        """
        url = "{}/v{}/packages/{}/{}/{}".format(self.url, self.api_version, document_status, page_no, records_per_page)
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        if 'x_search_text' in kwargs:
            headers['x-search-text'] = kwargs['x_search_text']
        return requests.get(url=url, headers=headers)

    def delete_package(self, package_id):
        """ Deleting a package.

        :param package_id: int; Package ID of the package you want to delete
        :return: response object
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}"
        headers = {
            "Authorization": "Bearer " + self.access_token,
            "Accept": "application/json",
            "Content": "application/json"
        }
        return requests.delete(url=url, headers=headers)

    def download_package(self, package_id:int, base_64=False, **kwargs) -> requests.Response:
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

    def open_document_package(self, package_id: int, **kwargs) -> requests.Response:
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

    def close_document_package(self, package_id: int) -> requests.Response:
        url = f"{self.url}/v{self.url}/packages/{package_id}/close"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
        }
        return requests.get(url=url, headers=headers)

    # Document workflow

    def get_workflow_details(self, package_id: int) -> requests.Response:
        """ Get the details of a specific workflow.

        :param package_id: int; Package ID of the package you want to get details on.
        :return: response object
        """
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/{workflow}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token,
        }
        return requests.get(url=url, headers=headers)

    def update_workflow_details(self, package_id: int, **kwargs) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = dict()
        if "workflow_mode" in kwargs:
            data["workflow_mode"] = kwargs["workflow_mode"]
        if "workflow_type" in kwargs:
            data["workflow_type"] = kwargs["workflow_type"]
        if "continue_on_decline" in kwargs:
            data["continue_on_decline"] = kwargs["continue_on_decline"]
        if "message" in kwargs:
            data["message"] = kwargs["message"]
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def get_workflow_history(self, package_id: int) -> requests.Response:
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/log"
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def get_process_evidence_report(self, package_id: int):
        url = "{}/v{}/packages/{}/report".format(self.url, self.api_version, package_id)
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    def add_users_to_workflow(self, package_id, user_email, user_name, role, **kwargs):
        """ Adding a user to a workflow.

        :param package_id: int; ID of the package the user should be added to.
        :param user_email: str; email address of the user whom should be added
        :param user_name: str; username of the user whom should be added
        :param role: str; role of the user in the workflow. Possible values include:  "SIGNER", "REVIEWER", "EDITOR","CARBON_COPY" or "INPERSON_HOST"
        :param kwargs:
            email_notifications: (bool)(optional); If set as true, SigningHub will send notifications to the user via email as per the document owner and user notification settings.  A value of false means no notifications will be sent to user throughout the workflow.
            signing_order: (int)(optional); Order of the recipient in the workflow. This signing order is mandatory when workflow type is "CUSTOM".
        :return: response object
        """
        url = "{}/v{}/packages/{}/workflow/users".format(self.url, self.api_version, package_id)
        headers = {
            "Authorization": "Bearer " + self.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        data = {
            'user_email': user_email,
            'user_name': user_name,
            'role': role,
        }
        if "email_notifications" in kwargs:
            data["email_notifications"] = kwargs["email_notifications"]
        if "signing_order" in kwargs:
            data["signing_order"] = kwargs["signing_order"]
        payload = list()
        payload.append(data)
        payload = json.dumps(payload)
        return requests.post(url=url, data=payload, headers=headers)

    def update_workflow_user(self, package_id: int, order: int, user_email: str, **kwargs):
        """ Updating a workflow user.

        :param package_id: int; ID of the package in which the user should be updated
        :param order: int; order of the user in the workflow
        :param user_email: str; email address of the user that needs to be updated
        :param kwargs:
            user_name: (str)(optional); Name of the recipient to be updated
            role: (str)(optional); Role of the recipient to be updated. Possible values are "SIGNER", "REVIEWER", "EDITOR","CARBON_COPY" or "INPERSON_HOST". If no value is provided, old value will be retained. However, while XML type document preparation, only supported role types are "SIGNER", "REVIEWER" and "CARBON_COPY"
            email_notifications: (bool)(optional); Setting its value to "true" sends an email notification to the user when its turn arrives in workflow. Setting its value to "false" does not send the email notification to the user on its turn. If no value is provided, old value will be retained.
            signing_order: (int)(optional); Order in which the workflow will be signed by the recipients. This signing order is important when workflow type is set to "CUSTOM".
        :return: response object
        """
        url = self.url + "/v3/packages/" + str(package_id) + "/workflow/" + str(order) + "/user"
        headers = {
            "Authorization": "Bearer " + self.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        data = {
            "user_email": user_email
        }
        if "user_name" in kwargs:
            data["user_name"] = kwargs["user_name"]
        if "role" in kwargs:
            data["role"] = kwargs["role"]
        if "email_notifications" in kwargs:
            data["email_notifications"] = kwargs["email_notifications"]
        if "signing_order" in kwargs:
            data["signing_order"] = kwargs["signing_order"]
        data = json.dumps(data)
        return requests.put(url=url, data=data, headers=headers)

    def add_groups_to_workflow(self, package_id: int, groupname: str, **kwargs):
        """ Adding pre-definded groups to a package workflow.

        :param package_id: int; ID of the package the group should be added to
        :param groupname: str; Name of the group that should be added to the workflow
        :param kwargs:
            role: (str)(optional) role of the group as a recipient in the workflow. Possible value are "SIGNER", "REVIEWER", "EDITOR","CARBON_COPY" and "INPERSON_HOST". However, while XML type document preparation, only supported role types are "SIGNER", "REVIEWER" and "CARBON_COPY"
            email_notifications: (bool)(optional); Setting its value to "true" sends an email notification to the user when its turn arrives in workflow. Setting its value to "false" does not send the email notification to the user on its turn. If no value is provided, default value of "true" will be set.
            siging_order (int)(optional); Order in which the workflow will be signed by the recipients. This signing order is important when workflow type is set to "CUSTOM".
        :return: response object
        """
        url = self.url + "/v3/packages/" + str(package_id) + "/workflow/groups"
        headers = {
            "Authorization": "Bearer " + self.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        data = {
            'group_name': groupname
        }
        if "role" in kwargs:
            data["role"] = kwargs["role"]
        if "email_notifications" in kwargs:
            data["email_notifications"] = kwargs["email_notifications"]
        if "signing_order" in kwargs:
            data["signing_order"] = kwargs["signing_order"]
        payload = list()
        payload.append(data)
        payload = json.dumps(payload)
        return requests.post(url=url, headers=headers, data=payload)

    def get_workflow_users(self, package_id: int):
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/users"
        headers = {
            "Authorization": "Bearer " + self.access_token,
            "Accept": "application/json"
        }
        return requests.get(url=url, headers=headers)

    def update_workflow_users_order(self, package_id: int, old_order: int, new_order: int):
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/workflow/{old_order}/reorder"
        headers = {
            "Authorization": "Bearer " + self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        data = {
            "order": new_order
        }
        data = json.dumps(data)
        return requests.put(url=url, headers=headers, data=data)

    def complete_workflow_in_the_middle(self, package_id: int):
        """

        :param package_id: int; Package ID of the workflow that needs to be completed.
        :return: response object
        """
        url = self.url + "/v3/packages/" + str(package_id) + "/complete"
        headers = {
            "Authorization": "Bearer " + self.access_token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        return requests.post(url=url, data=None, headers=headers)

    ### Document Preparation

    def get_document_fields(self, package_id: int, document_id: int, page_no: int):
        url = "{}/v{}/packages/{}/documents/{}/fields/{}".format(self.url, self.api_version,
                                                                               package_id, document_id, page_no)
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)

    # This call is api_version 3 only.
    def add_electronic_signature_field(self, package_id, document_id, order, page_no, **kwargs):
        url = "{}/v{}/packages/{}/documents/{}/fields/electronic_signature".format(self.url, self.api_version,
                                                                               package_id, document_id)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'order': order,
            'page_no': page_no,
            'dimensions': {},
            "authentication": {
                "enabled": False,
                "sms_otp": {
                    "enabled": False
                }
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

    # This call is api_version 4 only.
    def add_signature_field(self, package_id, document_id, order, page_no, **kwargs):
        url = f"{self.url}/v{self.api_version}/packages/{package_id}/documents/{document_id}/fields/signature"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            'order': order,
            'page_no': page_no
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
        if 'level_of_assurance' in kwargs:
            data['level_of_assurance'] = kwargs['level_of_assurance']
        data = json.dumps(data)
        return requests.post(url=url, data=data, headers=headers)

    def autoplace_fields(self, package_id: int, document_id: int, search_text: str, order: int, field_type: str, **kwargs):
        """ Autoplacing fields to a string in the document.

        :param package_id: int; ID of the package.
        :param document_id: int; ID of the document on which the fields should be added.
        :param search_text: str; text to which the fields should be added on the document.
        :param order: int; order of the user to which the fields should be assigned.
        :param field_type: Type of field to be created in the document. Possible values are "ELECTRONIC_SIGNATURE", "DIGITAL_SIGNATURE", "IN_PERSON_SIGNATURE", "INITIALS","TEXT", "NAME", "EMAIL", "COMPANY", "JOBTITLE", "RadioBox", "CheckBox", "DATE".
        :param kwargs:
            width: (int)(optional); width of the field in pixels
            height: (int)(optional); height of the field in pixels
            placement: (str)(optional): 	If the text is found, fields are to be placed in the document. Placement of the field can be mentioned in this attribute. Possible values of placement of a field are "LEFT", "RIGHT", "TOP", "BOTTOM". If no value is provided the default value will be "LEFT".
        :return: response object
        """
        url = self.url + "/v3/packages/" + str(package_id) + "/documents/" + str(document_id) + "/fields/autoplace"
        headers = {
            "Authorization": "Bearer " + self.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        data = {
            "search_text": search_text,
            "order": order,
            "field_type": field_type
        }
        if "width" in kwargs:
            data["dimensions"]["width"] = kwargs["width"]
        if "height" in kwargs:
            data["dimensions"]["height"] = kwargs["height"]
        if "placement" in kwargs:
            data["placement"] = kwargs["placement"]
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def delete_document_field(self, package_id: int, document_id: int, field_name: str):
        """ Deleting a field from a document.

        :param package_id: int; ID of the package.
        :param document_id: int; ID of the document where the field is placed.
        :param field_name: str; Name of the field which will be deleted.
        :return: response object
        """
        url = self.url + "/v3/packages/" + str(package_id) + "/documents/" + str(document_id) + "/fields"
        headers = {
            "Authorization": "Bearer " + self.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        data = {
            "field_name": field_name
        }
        data = json.dumps(data)
        return requests.delete(url=url, data=data, headers=headers)

    def sign_document(self, package_id: int, document_id: int, signature_field_name: str, **kwargs):
        url = "{}/v{}/packages/{}/documents/{}/sign".format(self.url, self.api_version, package_id, document_id)
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        data = {
            "field_name": signature_field_name
        }
        if 'x_otp' in kwargs:
            headers["x-otp"] = kwargs["x_otp"]
        if 'hand_signature_image' in kwargs:
            data["hand_signature_image"] = kwargs["hand_signature_image"]
        if 'user_password' in kwargs:
            data["user_password"] = kwargs["user_password"]
        if "signing_reason" in kwargs:
            data["signing_reason"] = kwargs["signing_reason"]
        if "signing_location" in kwargs:
            data["signing_location"] = kwargs["signing_location"]
        if "contact_information" in kwargs:
            data["contact_information"] = kwargs["contact_information"]
        if "user_name" in kwargs:
            data["user_name"] = kwargs["user_name"]
        if "appearance_design" in kwargs:
            data["appearance_design"] = kwargs["appearance_design"]
        if "signing_server" in kwargs:
            data["signing_server"] = kwargs["signing_server"]
        if "signing_capacity" in kwargs:
            data["signing_capacity"] = kwargs["signing_capacity"]
        if "skip_verification" in kwargs:
            data["skip_verification"] = kwargs["skip_verification"]
        data = json.dumps(data)
        return requests.post(url=url, headers=headers, data=data)

    def finish_processing(self, package_id: int):
        """ Call to finish processing a package. When signed via the API, a package needs a finish processing call to push the package to a "completed" status.

        :param package_id: int; ID of the package that needs to be finished
        :return: response object
        """
        url = "{}/v{}/packages/{}/finish".format(self.url, self.api_version, package_id)
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.post(url=url, headers=headers)

    # Personal Settings

    def get_general_profile_information(self):
        url = "{}/v{}/settings/profile".format(self.url, self.api_version)
        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self.access_token
        }
        return requests.get(url=url, headers=headers)
