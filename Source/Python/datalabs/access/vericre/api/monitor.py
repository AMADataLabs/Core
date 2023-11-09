""" Release endpoint classes."""
from dataclasses import dataclass
import logging

import urllib3

from datalabs.access.api.task import APIEndpointTask, ResourceNotFound, InternalServerError
from datalabs.access.vericre.api.authentication import EProfilesAuthenticatingEndpointMixin
from datalabs.access.vericre.api.header import PROFILE_HEADERS
from datalabs.parameter import add_schema
from datalabs.util.profile import parse_xml_to_dict, get_list_without_tags

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class HttpClient:
    HTTP = urllib3.PoolManager()


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

    def run(self):
        LOGGER.debug("Parameters in MonitorNotificationsEndpointTask: %s", self._parameters)

        access_token = self._get_eprofiles_access_token(self._parameters)

        notification_response = self._get_notifications(access_token)

        response_result = self._convert_response_to_json(notification_response)

        self._response_body = self._generate_response_body(response_result)

    def _get_notifications(self, access_token):
        response = self._request_notifications(access_token)

        if response.status == 204:
            raise ResourceNotFound("No notifications found.")

        if response.status != 200:
            raise InternalServerError(f"Internal Server error caused by: {response.reason}, status: {response.status}")

        return response

    def _convert_response_to_json(self, notification_response):
        converted_notifications = parse_xml_to_dict(notification_response.data)

        notification_list = get_list_without_tags(converted_notifications["monitor_notification_list"]["notifications"])

        return notification_list

    def _request_notifications(self, access_token):
        header = PROFILE_HEADERS.copy()
        header["Authorization"] = f"Bearer {access_token}"

        return self.HTTP.request("GET", f"{self._parameters.monitor_notification_url}", headers=header)

    @classmethod
    def _generate_response_body(cls, response):
        return response


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

    def run(self):
        LOGGER.debug("Parameters in MonitorProfilesEndpointTask: %s", self._parameters)

        access_token = self._get_eprofiles_access_token(self._parameters)

        monitor_profiles_response = self._get_profile_monitors(access_token)

        response_result = self._convert_response_to_json(monitor_profiles_response)

        self._response_body = response_result

    def _get_profile_monitors(self, access_token):
        response = self._request_monitors(access_token)

        if response.status == 204:
            raise ResourceNotFound("No profile monitors found.")

        if response.status != 200:
            raise InternalServerError(f"Internal Server error caused by: {response.reason}, status: {response.status}")

        return response

    def _convert_response_to_json(self, monitor_profiles_response):
        converted_monitors = parse_xml_to_dict(monitor_profiles_response.data)

        monitor_list = get_list_without_tags(converted_monitors["monitor_list"]["entries"])

        return monitor_list

    def _request_monitors(self, access_token):
        header = PROFILE_HEADERS.copy()
        header["Authorization"] = f"Bearer {access_token}"

        return self.HTTP.request("GET", f"{self._parameters.monitor_profile_url}", headers=header)
