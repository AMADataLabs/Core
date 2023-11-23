""" Release endpoint classes."""
from   dataclasses import dataclass
import logging
from   typing import List, Optional

import urllib3

from datalabs.access.api.task import APIEndpointTask, ResourceNotFound, InternalServerError
from datalabs.access.vericre.api.authentication import EProfilesAuthenticatingEndpointMixin
from datalabs.access.vericre.api.common import format_element_as_list
from datalabs.access.vericre.api.header import PROFILE_HEADERS
from datalabs.parameter import add_schema
from datalabs.util.xml import XMLToDictConverter

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class HttpClient:
    HTTP = urllib3.PoolManager()


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class MonitorEndpointParameters:
    method: str
    path: dict
    query: dict
    client_id: str
    client_secret: str
    token_url: str
    monitor_profile_url: str


class MonitorEndpointTask(EProfilesAuthenticatingEndpointMixin, APIEndpointTask, HttpClient):
    PARAMETER_CLASS = MonitorEndpointParameters

    def __init__(self, parameters: dict, data: Optional[List[bytes]] = None):
        super().__init__(parameters, data)
        self._http = urllib3.PoolManager()
        self._headers = PROFILE_HEADERS.copy()
        self._status = None

    def run(self):
        LOGGER.debug("Parameters in MonitorEndpointTask: %s", self._parameters)

        self._authenticate_to_eprofiles(self._parameters, self._headers)

        if self._parameters.method.upper() == 'PUT':
            monitor_profiles_response = self._make_profile_request()

        if self._parameters.method.upper() == 'DELETE':
            monitor_profiles_response = self._delete_profile_entities_monitors()

        self._generate_response(monitor_profiles_response)

    def _make_profile_request(self):
        entity_id = self._parameters.path["entity_id"]

        response = self._make_request_with_entity_id(entity_id)

        if response.status == 400:
            converted_error_message = XMLToDictConverter.parse_xml_to_dict(XMLToDictConverter(), response.data)

            error_message = format_element_as_list(converted_error_message["response_message"]["message"])

            raise ResourceNotFound(error_message)

        if response.status != 200:
            raise InternalServerError(f"Internal Server error caused by: {response.reason}, status: {response.status}")

        return response

    def _make_request_with_entity_id(self, entity_id):
        return self.HTTP.request("PUT", f"{self._parameters.monitor_profile_url}/{entity_id}", headers=self._headers)

    def _delete_profile_entities_monitors(self):
        response = self._request_profiles_monitor_entiries_delete()

        if response.status == 400:
            raise ResourceNotFound("Bad Request.")

        if response.status == 404:
            raise ResourceNotFound("No profile monitor entity found.")

        if response.status != 200:
            raise InternalServerError(f"Internal Server error caused by: {response.reason}, status: {response.status}")

        return response

    def _request_profiles_monitor_entiries_delete(self):
        entity_id = self._parameters.path["entity_id"]

        return self.HTTP.request(
            "DELETE", f"{self._parameters.monitor_profile_url}/{entity_id}", headers=self._headers
        )

    def _generate_response(self, response):
        self._status = response.status

        self._headers = {"Content-Type": "application/json"}


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class MonitorNotificationsEndpointParameters:
    method: str
    path: dict
    query: dict
    client_id: str
    client_secret: str
    token_url: str
    monitor_notification_url: str


class MonitorNotificationsEndpointTask(EProfilesAuthenticatingEndpointMixin, APIEndpointTask, HttpClient):
    PARAMETER_CLASS = MonitorNotificationsEndpointParameters

    def __init__(self, parameters: dict, data: Optional[List[bytes]] = None):
        super().__init__(parameters, data)
        self._http = urllib3.PoolManager()
        self._headers = PROFILE_HEADERS.copy()

    def run(self):
        LOGGER.debug("Parameters in MonitorNotificationsEndpointTask: %s", self._parameters)

        self._authenticate_to_eprofiles(self._parameters, self._headers)

        notification_response = self._get_notifications()

        response_result = self._convert_response_to_json(notification_response)

        self._generate_response(response_result)

    def _get_notifications(self):
        response = self._request_notifications()

        if response.status == 204:
            raise ResourceNotFound("No notifications found for this client ID.")

        if response.status != 200:
            raise InternalServerError(f"Internal Server error caused by: {response.reason}, status: {response.status}")

        return response

    @classmethod
    def _convert_response_to_json(cls, notification_response):
        converted_notifications = XMLToDictConverter.parse_xml_to_dict(XMLToDictConverter(), notification_response.data)

        notification_list = format_element_as_list(
            converted_notifications["monitor_notification_list"]["notifications"]
        )

        return notification_list

    def _generate_response(self, response):
        self._response_body = response

        self._headers = {"Content-Type": "application/json"}

    def _request_notifications(self):
        return self.HTTP.request("GET", self._parameters.monitor_notification_url, headers=self._headers)


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class MonitorNotificationUpdateEndpointParameters:
    method: str
    path: dict
    query: dict
    client_id: str
    client_secret: str
    token_url: str
    monitor_update_url: str
    monitor_delete_url: str


class MonitorNotificationUpdateEndpointTask(EProfilesAuthenticatingEndpointMixin, APIEndpointTask, HttpClient):
    PARAMETER_CLASS = MonitorNotificationUpdateEndpointParameters

    def __init__(self, parameters: dict, data: Optional[List[bytes]] = None):
        super().__init__(parameters, data)
        self._http = urllib3.PoolManager()
        self._headers = PROFILE_HEADERS.copy()

    def run(self):
        LOGGER.debug("Parameters in MonitorNotificationUpdateEndpointTask: %s", self._parameters)

        self._authenticate_to_eprofiles(self._parameters, self._headers)

        if self._parameters.method.upper() == 'POST':
            profile_response = self._update_notification()

        if self._parameters.method.upper() == 'DELETE':
            profile_response = self._delete_notification()

        response_result = self._convert_response_to_json(profile_response)

        self._generate_response(response_result)

    def _update_notification(self):
        response = self._request_update_notification()

        if response.status == 404:
            raise ResourceNotFound("Notification not found for the provided notification ID.")

        if response.status != 200:
            raise InternalServerError(f"Internal Server error caused by: {response.reason}, status: {response.status}")

        return response

    def _delete_notification(self):
        response = self._request_delete_notification()

        if response.status == 404:
            raise ResourceNotFound("Notification not found for the provided notification ID.")

        if response.status != 200:
            raise InternalServerError(f"Internal Server error caused by: {response.reason}, status: {response.status}")

        return response

    @classmethod
    def _convert_response_to_json(cls, profile_response):
        converted_profile = XMLToDictConverter.parse_xml_to_dict(XMLToDictConverter(), profile_response.data)

        return converted_profile["full_profile"]

    def _generate_response(self, response):
        self._response_body = response

        self._headers = {"Content-Type": "application/json"}

    def _request_update_notification(self):
        notification_id = self._parameters.path["notification_id"]

        return self.HTTP.request(
            "GET", f"{self._parameters.monitor_update_url}/{notification_id}", headers=self._headers
        )

    def _request_delete_notification(self):
        notification_id = self._parameters.path["notification_id"]

        return self.HTTP.request(
            "DELETE", f"{self._parameters.monitor_delete_url}/{notification_id}", headers=self._headers
        )


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class MonitorProfilesEndpointParameters:
    method: str
    path: dict
    query: dict
    client_id: str
    client_secret: str
    token_url: str
    monitor_profile_url: str


class MonitorProfilesEndpointTask(EProfilesAuthenticatingEndpointMixin, APIEndpointTask, HttpClient):
    PARAMETER_CLASS = MonitorProfilesEndpointParameters

    def __init__(self, parameters: dict, data: Optional[List[bytes]] = None):
        super().__init__(parameters, data)
        self._http = urllib3.PoolManager()
        self._headers = PROFILE_HEADERS.copy()

    def run(self):
        LOGGER.debug("Parameters in MonitorProfilesEndpointTask: %s", self._parameters)

        self._authenticate_to_eprofiles(self._parameters, self._headers)

        monitor_profiles_response = self._get_profile_monitors()

        response_result = self._convert_response_to_json(monitor_profiles_response)

        self._generate_response(response_result)

    def _get_profile_monitors(self):
        response = self._request_monitors()

        if response.status == 204:
            raise ResourceNotFound("No profile monitors found.")

        if response.status != 200:
            raise InternalServerError(f"Internal Server error caused by: {response.reason}, status: {response.status}")

        return response

    @classmethod
    def _convert_response_to_json(cls, monitor_profiles_response):
        converted_monitors = XMLToDictConverter.parse_xml_to_dict(XMLToDictConverter(), monitor_profiles_response.data)

        monitor_list = format_element_as_list(converted_monitors["monitor_list"]["entries"])

        return monitor_list

    def _request_monitors(self):
        return self.HTTP.request("GET", f"{self._parameters.monitor_profile_url}", headers=self._headers)

    def _generate_response(self, response):
        self._response_body = response

