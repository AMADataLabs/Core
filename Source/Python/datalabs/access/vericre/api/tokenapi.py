import json
from dataclasses import dataclass

import urllib3
import logging
import urllib.parse

from datalabs.access.api.task import APIEndpointTask, InternalServerError
from datalabs.parameter import add_schema
from datalabs.util.profile import run_time_logger

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class HttpClient:
    HTTP = urllib3.PoolManager()


@add_schema(unknowns=True)
@dataclass
# pylint: disable=too-many-instance-attributes
class AMATokenEndpointParameters:
    method: str
    path: dict
    query: dict
    token_url: str


class AMATokenEndpointTask(APIEndpointTask, HttpClient):
    PARAMETER_CLASS = AMATokenEndpointParameters

    def run(self):
        LOGGER.debug('Parameters in AMATokenEndpointTask: %s', self._parameters)

        access_token = self._get_ama_access_token()
        LOGGER.debug("access_token: %s", access_token)
        self._generate_response(access_token)

    @run_time_logger
    def _get_ama_access_token(self):
        token_headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        token_fields = {
            "grant_type": self._parameters.query.get("grant_type"),
            "client_id": self._parameters.query.get("client_id"),
            "client_secret": self._parameters.query.get("client_secret"),
        }

        token_body = urllib.parse.urlencode(token_fields)
        LOGGER.debug("token_body: %s", token_body)
        token_response = self._request_ama_token(token_headers, token_body)

        if token_response.status != 200:
            raise InternalServerError(
                f'Internal Server error caused by: {token_response.data}, status: {token_response.status}'
            )

        token_json = json.loads(token_response.data.decode("utf-8"))

        return token_json['access_token']

    def _generate_response(self, response):
        self._response_body = self._generate_response_body(response)
        self._headers = self._generate_headers(response)

    @classmethod
    def _generate_response_body(cls, response):
        return response.data

    @run_time_logger
    def _request_ama_token(self, token_headers, token_body):
        return self.HTTP.request(
            'POST',
            "https://wsextstage.ama-assn.org/oauth2/endpoint/eprofilesprovider/token",
            headers=token_headers,
            body=token_body
        )
