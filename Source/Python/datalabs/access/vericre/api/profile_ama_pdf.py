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
class AMAProfilePDFEndpointParameters:
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


class AMAProfilePDFEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = AMAProfilePDFEndpointParameters

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)
        entity_id = self._parameters.path.get('entityId')

        response_result = f"AMAProfilePDFEndpointTask, request with parameter: entityId={entity_id}"
        self._response_body = self._generate_response_body(response_result)
    
    @classmethod
    def _generate_response_body(cls, response_result):
        return {"result": response_result}