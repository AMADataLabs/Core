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

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        self._run()

        
    
    def _run(self):
        pass

    @classmethod
    def _generate_response_body(cls, response_result):
        
        return {"result": response_result}


class GetProfilesEndpointTask(BaseProfileEndpointTask):
    
    def _run(self):
        response_result = "GetProfilesEndpointTask success"
        self._response_body = self._generate_response_body(response_result)
    

class SingleProfileEndpointTask(BaseProfileEndpointTask):
    def _run(self):
        entityId = self._parameters.path.get('entityId')
        
        response_result = f"SingleProfileEndpointTask, request with parameter: entityId={entityId}"
        self._response_body = self._generate_response_body(response_result)


class PatchProfilesEndpointTask(BaseProfileEndpointTask):
    def _run(self):
        response_result = "PatchProfilesEndpointTask success"
        self._response_body = self._generate_response_body(response_result)