""" Release endpoint classes."""
from   dataclasses import dataclass
import logging

from   datalabs.access.api.task import APIEndpointTask
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class ProfilesEndpointParameters:
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


class BaseProfileEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = ProfilesEndpointParameters

    def __init__(self, parameters: dict, data: "list<bytes>"=None):
        super().__init__(parameters, data)

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        self._run()
    
    def _run(self):
        pass

    @classmethod
    def _generate_response_body(cls, response_result):
        return {"result": response_result}


class ProfilesEndpointTask(BaseProfileEndpointTask):
    
    def _run(self):
        method = self._parameters.method

        response_result = f"ProfilesEndpointTask success, method: {method}"
        self._response_body = self._generate_response_body(response_result)
    

class ProfileEndpointTask(BaseProfileEndpointTask):
    def _run(self):
        entity_id = self._parameters.path.get('entityId')
        
        response_result = f"ProfileEndpointTask, request with parameter: entityId={entity_id}"
        self._response_body = self._generate_response_body(response_result)