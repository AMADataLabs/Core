""" Release endpoint classes."""
from   dataclasses import dataclass
import logging

import boto3
from   botocore.exceptions import ClientError

from   datalabs.access.api.task import APIEndpointTask, InternalServerError
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
    unknowns: dict=None


class ProfilesEndpointTask(APIEndpointTask):
    PARAMETER_CLASS = ProfilesEndpointParameters

    def __init__(self, parameters: dict, data: "list<bytes>"=None):
        super().__init__(parameters, data)

        self._s3 = boto3.client('s3')

    def run(self):
        print("profile app initial===")

        self._response_body = self._generate_response_body("body-profile")

    @classmethod
    def _generate_response_body(cls, msg):
        return f'profile app response{msg}'
