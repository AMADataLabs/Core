""" Release endpoint classes."""
from   abc import abstractmethod
from   dataclasses import dataclass, asdict
import logging
import requests
import threading
import time

from   sqlalchemy import case, literal

from   datalabs.access.api.task import APIEndpointTask, ResourceNotFound
from   datalabs.access.orm import Database
from   datalabs.model.vericre.api import Form, FormField, FormSection, FormSubSection, Physician, User
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

        threading.Thread(target=self._demo_for_threading).start()

        response_result = f"---{self._parameters.backend_domain}"
        LOGGER.info('do something with response_result')

        self._response_body = self._generate_response_body(response_result)

    def _demo_for_threading(self):
        LOGGER.info('Demo for threading start...')
        time.sleep(5)
        api_invoke_result = requests.get(f'https://localhost:4443', verify=False)
        #api_invoke_result = requests.get(f'https://{self._parameters.backend_domain}')
        LOGGER.info('API invoke result: %s', api_invoke_result.content)

    @classmethod
    def _generate_response_body(cls, response_result):
        return response_result
