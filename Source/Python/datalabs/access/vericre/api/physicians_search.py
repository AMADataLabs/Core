""" Release endpoint classes."""
from   dataclasses import dataclass
import logging

from   datalabs.access.api.task import APIEndpointTask
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema(unknowns=True)
@dataclass
class PhysiciansSearchEndpointParameters:
    method: str
    path: dict
    query: dict
    authorization: dict
    database_name: str
    database_backend: str
    database_host: str
    database_port: str
    database_username: str
    database_password: str
    unknowns: dict=None


class PhysiciansSearchEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = PhysiciansSearchEndpointParameters

    def __init__(self, parameters: dict, data: "list<bytes>"=None):
        super().__init__(parameters, data)

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        response_result = "PhysiciansSearchEndpointTask success"
        self._response_body = self._generate_response_body(response_result)
    
    @classmethod
    def _generate_response_body(cls, response_result):
        return {"result": response_result}