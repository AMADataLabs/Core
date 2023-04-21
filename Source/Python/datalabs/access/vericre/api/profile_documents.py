""" Release endpoint classes."""
from   dataclasses import dataclass
import logging

from   datalabs.access.api.task import APIEndpointTask
from   datalabs.access.aws import AWSClient
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

    def run(self):
        LOGGER.debug('Parameters: %s', self._parameters)
        entity_id = self._parameters.path.get('entityId')

        with AWSClient('s3') as s3:
            files_info = self._get_files(s3)

        print(files_info)

        response_result = f"ProfileDocumentsEndpoint, request with parameter: entityId={entity_id}"
        self._response_body = self._generate_response_body(response_result)
    
    def _get_files(self, s3):
        response = s3.list_objects_v2(Bucket='ama-sbx-vericre-us-east-1', Prefix='15d2a16c-753d-4e82-b5b7-1659b074b3ed/Avatar')
        objects = {x['Key'].split('/', 3)[2] for x in response['Contents']}

        print(objects)
        if  '' in objects:
            objects.remove('')

        return objects
    
    @classmethod
    def _generate_response_body(cls, response_result):
        return {"result": response_result}