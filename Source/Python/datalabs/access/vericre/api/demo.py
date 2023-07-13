""" Release endpoint classes."""
from   dataclasses import dataclass
import logging

import requests

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
        
        try:
            requests.get(f'https://{self._parameters.vericre_alb_domain}', verify=False, timeout=(2, 0.1))
        except requests.exceptions.ReadTimeout:
            LOGGER.info('Timeout as expected')

    @classmethod
    def _generate_response_body(cls, response_result):
        return response_result
