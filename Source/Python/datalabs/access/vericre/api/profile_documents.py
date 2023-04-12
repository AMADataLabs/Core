""" Release endpoint classes."""
from   dataclasses import dataclass
import logging

import boto3

from   datalabs.access.api.task import APIEndpointTask
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=too-many-instance-attributes
@add_schema(unknowns=True)
@dataclass
class ProfileDocumentsEndpointParameters:
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


class ProfileDocumentsEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = ProfileDocumentsEndpointParameters

    def __init__(self, parameters: dict, data: "list<bytes>"=None):
        super().__init__(parameters, data)

        self._s3 = boto3.client('s3')

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)
        entityId = self._parameters.path.get('entityId')

        response_result = f"ProfileDocumentsEndpoint, request with parameter: entityId={entityId}"
        self._response_body = self._generate_response_body(response_result)
    
    @classmethod
    def _generate_response_body(cls, response_result):
        
        return {"result": response_result}
