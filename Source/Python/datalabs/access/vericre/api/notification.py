""" Release endpoint classes."""
from dataclasses import dataclass

import logging

import urllib3

from datalabs.access.api.task import APIEndpointTask
from datalabs.parameter import add_schema
from datalabs.util.profile import get_ama_access_token

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
    token_url: str


class MonitorNotificationsEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = MonitorNotificationsEndpointParameters

    def run(self):
        LOGGER.debug('Parameters in MonitorNotificationsEndpointTask: %s', self._parameters)
        grant_type = self._parameters.query["grant_type"][0]
        client_id = self._parameters.query["client_id"][0]
        client_secret = self._parameters.query["client_secret"][0]

        token_json = get_ama_access_token(self, grant_type, client_id, client_secret)

        self._response_body = token_json
