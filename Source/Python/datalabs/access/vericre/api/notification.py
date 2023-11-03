""" Release endpoint classes."""
from   dataclasses import dataclass
import logging

import urllib3

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound, InternalServerError
from   datalabs.parameter import add_schema
from   datalabs.util.profile import get_ama_access_token, parse_xml_to_dict

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class HttpClient:
    HTTP = urllib3.PoolManager()


class StaticTaskParameters:
    PROFILE_HEADERS = {
        'X-Location': 'Sample Vericre',
        'X-CredentialProviderUserId': "1",
        'X-SourceSystem': "1"
    }


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
    notification_url: str


class MonitorNotificationsEndpointTask(APIEndpointTask, HttpClient):
    PARAMETER_CLASS = MonitorNotificationsEndpointParameters

    def run(self):
        LOGGER.debug('Parameters in MonitorNotificationsEndpointTask: %s', self._parameters)

        access_token = get_ama_access_token(self._parameters)

        StaticTaskParameters.PROFILE_HEADERS['Authorization'] = f'Bearer {access_token}'

        notification_response = self._get_notifications()

        response_result = self._convert_response_to_json(notification_response)

        self._response_body = self._generate_response_body(response_result)

    def _get_notifications(self):
        response = self._request_notifications()

        if response.status == 204:
            raise ResourceNotFound('No notifications found.')

        if response.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {response.reason}, status: {response.status}'
            )

        return response

    def _convert_response_to_json(self, notification_response):
        converted_notifications = parse_xml_to_dict(notification_response.data)

        notification_list = self._get_notifications_list(converted_notifications)

        return notification_list

    def _get_notifications_list(self, converted_notifications):
        notifications = converted_notifications['monitorNotificationList']['notifications']
        notification_list = []

        if isinstance(notifications, dict):
            notification_list.append(notifications)
        else:
            notification_list = notifications

        return notification_list

    def _request_notifications(self):
        return self.HTTP.request(
            'GET',
            f'{self._parameters.notification_url}',
            headers=StaticTaskParameters.PROFILE_HEADERS
        )

    @classmethod
    def _generate_response_body(cls, response):
        return response
