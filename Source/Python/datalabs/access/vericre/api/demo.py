""" Release endpoint classes."""
from   dataclasses import dataclass
import logging
import threading

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
    backend_domain: str
    unknowns: dict=None


class DemoEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = DemoEndpointParameters

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        thread = threading.Thread(target=self._demo_for_threading)
        thread.start()

        response_result = f"---{self._parameters.backend_domain}"
        LOGGER.info('do something with response_result')

        self._response_body = self._generate_response_body(response_result)

    def _demo_for_threading(self):
        LOGGER.info('Demo for threading start...')
        
        api_invoke_result = requests.get(f'https://{self._parameters.vericre_alb_domain}', verify=False)
        LOGGER.info('API invoke result: %s', api_invoke_result.content)

        for num in range(100):
            LOGGER.info('Demo for threading counter: %s', num)

    @classmethod
    def _generate_response_body(cls, response_result):
        return response_result
