import json
import requests
from signinghubapi.signinghubapi import Connection


class Package:
    def __init__(self, package_id: int, workflow_details=None):
        self._id = package_id
        self._documents = list()
        self._name = None
        self._owner = None
        self._owner_name = None
        self._status = None
        self._folder = None
        self._next_signer = None
        self._next_signer_email = list()
        self._uploaded_on = None
        self._modified_on = None
        self._workflow_type = None
        self._continue_on_decline = None
        self._workflow_status = None
        self._workflow_mode = None
        self._message = None
        self._read_only = None
        self._post_process = dict()
        self._signers = list()
        self._reviewers = list()
        self._carbon_copy = list()
        self._users = list()
        if workflow_details:
            self.set_workflow_details(workflow_details)

    def __str__(self):
        return f'Package with ID {self.id}'

    @property
    def id(self):
        return self._id

    @property
    def documents(self):
        return self._documents

    @property
    def owner(self):
        return self._owner

    @property
    def owner_name(self):
        return self._owner_name

    @property
    def status(self):
        return self._status

    @property
    def folder(self):
        return self._folder

    @property
    def next_signer(self):
        return self._next_signer

    @property
    def next_signer_email(self):
        return self._next_signer_email

    @property
    def uploaded_on(self):
        return self._uploaded_on

    @property
    def modified_on(self):
        return self._modified_on

    @property
    def workflow_type(self):
        return self._workflow_type

    @property
    def continue_on_decline(self):
        return self._continue_on_decline

    @property
    def workflow_status(self):
        return self._workflow_status

    @property
    def workflow_mode(self):
        return self._workflow_mode

    @property
    def message(self):
        return self._message

    @property
    def read_only(self):
        return self._read_only

    @property
    def post_process(self):
        return self._post_process

    @property
    def signers(self):
        return self._signers

    @property
    def reviewers(self):
        return self._reviewers

    @property
    def carbon_copy(self):
        return self._carbon_copy

    @property
    def users(self):
        return self._users

    @id.setter
    def id(self, new_id):
        self._id = new_id

    def set_workflow_details(self, workflow_details_json: dict):
        self._id = workflow_details_json["package_id"]
        self._name = workflow_details_json["package_name"]
        self._owner = User(user_email=workflow_details_json["package_owner"], user_name=workflow_details_json["owner_name"])
        self._owner_name = workflow_details_json["owner_name"]
        self._status = workflow_details_json["package_status"]
        self._folder = workflow_details_json["folder"]
        self._next_signer = workflow_details_json["next_signer"]
        self._next_signer_email.clear()
        for signer in workflow_details_json["next_signer_email"]:
            self._next_signer_email.append(signer)
        self._uploaded_on = workflow_details_json["uploaded_on"]
        self._modified_on = workflow_details_json["modified_on"]
        self._workflow_type = workflow_details_json["workflow"]["workflow_type"]
        self._continue_on_decline = workflow_details_json["workflow"]["continue_on_decline"]
        self._status = workflow_details_json["package_status"]
        self._workflow_mode = workflow_details_json["workflow"]["workflow_mode"]
        self._message = workflow_details_json["workflow"]["message"]
        self._read_only = workflow_details_json["workflow"]["message"]
        self._post_process = workflow_details_json["workflow"]["post_process"]
        self._documents = list()
        for document in workflow_details_json["documents"]:
            self._documents.append(Document(package=self, document_id=document["document_id"], workflow_details=workflow_details_json))
        self._signers = list()
        self._reviewers = list()
        self._carbon_copy = list()
        self._users = list()
        for person in workflow_details_json["users"]:
            if person["role"] == "SIGNER":
                self._signers.append(person)
            if person["role"] == "REVIEWER":
                self._reviewers.append(person)
            if person["role"] == "CARBON_COPY":
                self._carbon_copy.append(person)
            self._users.append(Recipient(workflow_details_user_json=person))

    def set_users(self, get_workflow_users_json):
        for person in get_workflow_users_json:
            if person["role"] == "SIGNER":
                self._signers.append(person)
            if person["role"] == "REVIEWER":
                self._reviewers.append(person)
            if person["role"] == "CARBON_COPY":
                self._carbon_copy.append(person)
            self._users.append(Recipient(workflow_details_user_json=person))

    def fetch_info_and_set_details(self, connection: Connection):
        if not self.id:
            raise ValueError("Package ID is None")
        if type(self.id) is not int:
            raise TypeError(f"Package ID is not of type int, instead it is {type(self.id)}")
        call = connection.get_workflow_details(self.id)
        if call.status_code != 200:
            raise ConnectionError(f"Get workflow details call did not return 200: it returned {call.status_code} with message {call.text}")
        workflow_details_json = json.loads(call.text)
        if not workflow_details_json:
            raise TypeError("Workflow details is empty")
        self.set_workflow_details(workflow_details_json)

    def share_call(self, connection: Connection) -> requests.Response:
        if self.status != "DRAFT":
            raise ValueError(f"Package status is not set to DRAFT. Package cannot be shared.")
        return connection.share_document_package(self.id)

    def get_workflow_details_call(self, connection: Connection) -> requests.Response:
        call = connection.get_workflow_details(self.id)
        if call.status_code == 200:
            self.set_workflow_details(json.loads(call.text))
        return call

    def get_workflow_users_call(self, connection: Connection) -> requests.Response:
        call = connection.get_workflow_users(self.id)
        if call.status_code == 200:
            self.set_users(json.loads(call.text))
        return call


class Document:
    def __init__(self, package: Package, document_id: int, workflow_details=None):
        self._id = document_id
        self._package = package
        self._name = None
        self._type = None
        self._order = 0
        self._source = None
        self._height = 0
        self._width = 0
        self._number_of_pages = 0
        self._created_on = None
        self._modified_on = None
        self._form_fields = None
        self._template = None
        self._certify = dict()
        self._lock_form_fields = None
        self._locked = None
        self._page_properties = dict()
        self._pages = list()
        if workflow_details:
            self.set_document_details(workflow_details)

    def __str__(self):
        return f'Document with ID {self.id}'

    @property
    def id(self):
        return self._id

    @property
    def package(self):
        return self._package

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def order(self):
        return self._order

    @property
    def source(self):
        return self._source

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    @property
    def number_of_pages(self):
        return self._number_of_pages

    @property
    def created_on(self):
        return self._created_on

    @property
    def modified_on(self):
        return self._modified_on

    @property
    def form_fields(self):
        return self._form_fields

    @property
    def template(self):
        return self._template

    @property
    def certify(self):
        return self._certify

    @property
    def lock_form_fields(self):
        return self._lock_form_fields

    @property
    def locked(self):
        return self._locked

    @property
    def page_properties(self):
        return self._page_properties

    @property
    def pages(self):
        return self._pages

    @id.setter
    def id(self, new_id):
        self._id = new_id

    def set_document_details(self, workflow_details_json: dict):
        for document in workflow_details_json["documents"]:
            if self.id == document["document_id"]:
                self._name = document["document_name"]
                self._type = document["document_type"]
                self._order = document["document_order"]
                self._source = document["document_source"]
                self._height = document["document_height"]
                self._width = document["document_width"]
                self._number_of_pages = document["document_pages"]
                self._created_on = document["created_on"]
                self._modified_on = document["modified_on"]
                self._form_fields = document["form_fields"]
                self._template = document["template"]
                self._certify["enabled"] = document["certify"]["enabled"]
                self._certify["allowed_permissions"] = document["certify"]["allowed_permissions"]
                self._certify["default_permission"] = document["certify"]["default_permission"]
                self._lock_form_fields = document["lock_form_fields"]
                self._locked = document["locked"]
                for page in range(1, self._number_of_pages + 1):
                    self._pages.append(Page(package=self.package, document=self, page_number=page))

    def get_document_fields_call(self, connection: Connection, page_number: int):
        if page_number > self.number_of_pages:
            raise ValueError("page_number cannot be greater than the total number of pages")
        return connection.get_document_fields(package_id=self.package.id, document_id=self.id, page_no=page_number)

    def set_page_fields(self, connection: Connection):
        for page in range(1, self.number_of_pages + 1):
            get_fields_call = self.get_document_fields_call(connection=connection, page_number=page)
            if get_fields_call.status_code == 200:
                self.page_properties[page] = json.loads(get_fields_call.text)


class Page:
    def __init__(self, package: Package, document: Document, page_number: int):
        self._package = package
        self._document = document
        self._number = page_number
        self._fields = dict()

    @property
    def fields(self):
        return self._fields

    @property
    def number(self):
        return self._number

    def set_fields(self, connection: Connection):
        get_fields_call = connection.get_document_fields(self._package.id, self._document.id, self.number)
        if get_fields_call.status_code == 200:
            self._fields = json.loads(get_fields_call.text)
        else:
            self._fields = dict()
            raise ConnectionError("Get document fields call did not return 200")


class User:
    def __init__(self, user_email=None, user_name=None, general_profile_information_json=None):
        if not user_email and not general_profile_information_json:
            raise ValueError("Both user_email and general_profile_information_json cannot be None")
        if not user_email:
            self.set_general_profile_information(general_profile_information_json)
        else:
            self._email = user_email
            self._name = user_name
            self._job_title = None
            self._company_name = None
            self._mobile_number = None
            self._enterprise_role = None
            self._ra_userid = None
            self._user_national_id = None
            self._security_question = None
            self._country = None
            self._timezone = None
            self._language = None
            self._enterprise_name = None
            self._enterprise_owner = None
            self._enterprise_owner_email = None
            self._enterprise_mobile_number = None

    @property
    def email(self):
        return self._email

    @property
    def name(self):
        return self._name

    @property
    def job_title(self):
        return self._job_title

    @property
    def company_name(self):
        return self._company_name

    @property
    def mobile_number(self):
        return self._mobile_number

    @property
    def enterprise_role(self):
        return self._enterprise_role

    @property
    def ra_userid(self):
        return self._ra_userid

    @property
    def user_national_id(self):
        return self._user_national_id

    @property
    def security_question(self):
        return self._security_question

    @property
    def country(self):
        return self._country

    @property
    def timezone(self):
        return self._timezone

    @property
    def language(self):
        return self._language

    @property
    def enterprise_name(self):
        return self._enterprise_name

    @property
    def enterprise_owner(self):
        return self._enterprise_owner

    @property
    def enterprise_owner_email(self):
        return self._enterprise_owner_email

    @property
    def enterprise_mobile_number(self):
        return self._enterprise_mobile_number

    @email.setter
    def email(self, new_user_email):
        self._email = new_user_email

    def set_general_profile_information(self, general_profile_information_json):
        self._email = general_profile_information_json["general"]["user_email"]
        self._name = general_profile_information_json["general"]["user_name"]
        self._job_title = general_profile_information_json["general"]["job_title"]
        self._company_name = general_profile_information_json["general"]["company_name"]
        self._mobile_number = general_profile_information_json["general"]["mobile_number"]
        self._enterprise_role = general_profile_information_json["general"]["enterprise_role"]
        self._ra_userid = general_profile_information_json["general"]["ra_userid"]
        self._user_national_id = general_profile_information_json["general"]["user_national_id"]
        self._security_question = general_profile_information_json["security"]["question"]
        self._country = general_profile_information_json["locale"]["country"]
        self._timezone = general_profile_information_json["locale"]["timezone"]
        self._language = general_profile_information_json["locale"]["language"]
        self._enterprise_name = SigningHubEnterprise(general_profile_information_json=general_profile_information_json)
        self._enterprise_owner = User(user_email=general_profile_information_json["enterprise"]["owner_email"], user_name=general_profile_information_json["enterprise"]["owner"])
        self._enterprise_owner_email = general_profile_information_json["enterprise"]["owner_email"]
        self._enterprise_mobile_number = general_profile_information_json["enterprise"]["mobile_number"]

    def get_general_profile_information_call(self, connection: Connection):
        call = connection.get_general_profile_information()
        if call.status_code == 200:
            self.set_general_profile_information(general_profile_information_json=json.loads(call.text))
        return call


class Recipient:
    def __init__(self, user_email=None, group_name=None, workflow_details_user_json=None):
        if workflow_details_user_json:
            self.set_details(workflow_details_user_json)
        else:
            self._email = user_email
            self._name = None
            self._group_name = group_name
            self._group_members = None
            self._role = None
            self._order = None
            self._signing_order = None
            self._is_user = False
            self._is_group = False
            if workflow_details_user_json:
                self.set_details(workflow_details_user_json)

    @property
    def email(self):
        return self._email

    @property
    def name(self):
        return self._name

    @property
    def group_name(self):
        return self._group_name

    @property
    def group_members(self):
        return self._group_members

    @property
    def role(self):
        return self._role

    @property
    def order(self):
        return self._order

    @property
    def signing_order(self):
        return self._signing_order

    @property
    def is_user(self):
        return self._is_user

    @property
    def is_group(self):
        return self._is_group

    def set_details(self, workflow_details_user_json: dict):
        self._email = workflow_details_user_json["user_email"]
        self._name = workflow_details_user_json["user_name"]
        self._group_name = workflow_details_user_json["group_name"]
        self._group_members = workflow_details_user_json["group_members"]
        self._role = workflow_details_user_json["role"]
        self._order = workflow_details_user_json["order"]
        self._signing_order = workflow_details_user_json["signing_order"]
        if workflow_details_user_json["user_email"]:
            self._is_user = True
        if workflow_details_user_json["group_name"]:
            self._is_group = True


class SigningHubEnterprise:
    def __init__(self, enterprise_name=None, general_profile_information_json=None):
        if not enterprise_name and not general_profile_information_json:
            raise ValueError("Both enterprise name and general profile information json cannot be None")
        self._name = enterprise_name
        self._owner_email = None
        self._owner_name = None
        if general_profile_information_json:
            self.set_details(general_profile_information_json)

    @property
    def name(self):
        return self._name

    @property
    def owner_email(self):
        return self._owner_email

    @property
    def owner_name(self):
        return self._owner_name

    def set_details(self, general_profile_information_json: dict):
        self._name = general_profile_information_json["enterprise"]["enterprise_name"]
        self._owner_email = general_profile_information_json["enterprise"]["owner_email"]
        self._owner_name = general_profile_information_json["enterprise"]["owner"]
