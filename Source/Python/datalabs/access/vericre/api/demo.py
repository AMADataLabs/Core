""" Release endpoint classes."""
from   dataclasses import dataclass
import logging

import requests
import threading

from   datalabs.access.api.task import APIEndpointTask
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class DemoEndpointParameters:
    method: str
    path: dict
    query: dict
    authorization: dict
    vericre_alb_domain: str
    unknowns: dict=None


class DemoEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = DemoEndpointParameters

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        self._demo_for_threading()

        response_result = f"---{self._parameters.vericre_alb_domain}"
        LOGGER.info('do something with response_result')

        self._response_body = self._generate_response_body(response_result)

    def _demo_for_threading(self):
        LOGGER.info('Demo for threading start...')
        
        physicians = [
            {"entityId":"1689898","npiNumber":"1275562779"},
            {"entityId":"1689899","npiNumber":"1275562778"}
        ]

        self._request_caqh_sync(physicians)

    def _request_caqh_sync(self, physicians):
        try:
            requests.post(
                f'https://{self._parameters.vericre_alb_domain}',
                verify=False,
                timeout=(None, 0.1),
                json=physicians
            )
        except requests.exceptions.ReadTimeout:
            LOGGER.info('CAQH sync request sent: %s', len(physicians))

    @classmethod
    def _generate_response_body(cls, response_result):
        return response_result
