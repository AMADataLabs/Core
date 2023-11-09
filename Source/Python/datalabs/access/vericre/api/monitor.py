""" Release endpoint classes."""
from dataclasses import dataclass
import logging
from typing import List, Optional

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

    def __init__(self, parameters: dict, data: Optional[List[bytes]] = None):
        super().__init__(parameters, data)
        self._http = urllib3.PoolManager()
        self._headers = PROFILE_HEADERS.copy()

    def run(self):
        LOGGER.debug('Parameters in MonitorNotificationsEndpointTask: %s', self._parameters)

        self._authenticate_to_eprofiles(self._parameters, self._headers)

        notification_response = self._get_notifications()

        response_result = self._convert_response_to_json(notification_response)

        self._generate_response(response_result)

    def _get_notifications(self):
        response = self._request_notifications()

        if response.status == 204:
            raise ResourceNotFound('No notifications found.')

        if response.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {response.reason}, status: {response.status}'
            )

        return response

    @classmethod
    def _convert_response_to_json(cls, notification_response):
        converted_notifications = parse_xml_to_dict(notification_response.data)

        notification_list = get_list_without_tags(converted_notifications['monitor_notification_list']['notifications'])

        return notification_list

    def _request_notifications(self):
        return self.HTTP.request(
            'GET',
            f'{self._parameters.monitor_notification_url}',
            headers=self._headers
        )

    def _generate_response(self, response):
        self._response_body = response

        self._headers = {"Content-Type": "application/json"}


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
        LOGGER.debug('Parameters in MonitorProfilesEndpointTask: %s', self._parameters)

        self._authenticate_to_eprofiles(self._parameters, self._headers)

        monitor_profiles_response = self._get_profile_monitors()

        response_result = self._convert_response_to_json(monitor_profiles_response)

        self._generate_response(response_result)

    def _get_profile_monitors(self):
        response = self._request_monitors()

        if response.status == 204:
            raise ResourceNotFound('No profile monitors found.')

        if response.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {response.reason}, status: {response.status}'
            )

        return response

    @classmethod
    def _convert_response_to_json(cls, monitor_profiles_response):
        converted_monitors = parse_xml_to_dict(monitor_profiles_response.data)

        monitor_list = get_list_without_tags(converted_monitors['monitor_list']['entries'])

        return monitor_list

    def _request_monitors(self):
        return self.HTTP.request(
            'GET',
            f'{self._parameters.monitor_profile_url}',
            headers=self._headers
        )

    def _generate_response(self, response):
        self._response_body = response

        self._headers = {"Content-Type": "application/json"}
