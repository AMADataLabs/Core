""" Release endpoint classes."""
from   dataclasses import dataclass
import logging

import boto3

from   datalabs.access.api.task import APIEndpointTask
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema(unknowns=True)
@dataclass
class PhysiciansSearchEndpointParameters:
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

        self._s3 = boto3.client('s3')

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)

        response_result = "PhysiciansSearchEndpointTask success"
        self._response_body = self._generate_response_body(response_result)
    
    @classmethod
    def _generate_response_body(cls, response_result):
        
        return {"result": response_result}