"""AWS DynamoDB Loader"""
import json
import logging
import boto3
from   dataclasses import dataclass

from   opensearchpy import OpenSearch, RequestsHttpConnection
from   requests_aws4auth import AWS4Auth

from   datalabs.parameter import add_schema
from   datalabs.task import Task


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class OpenSearchLoaderParameters:
    index_name: str
    index_host: str
    execution_time: str = None
    region: str = 'us-east-1'


class OpensearchLoaderTask(Task):
    PARAMETER_CLASS = OpenSearchLoaderParameters

    def run(self):
        LOGGER.debug('Input data: \n%s', self._data)
        knowledge_base_data = json.loads(self._data[0].decode())
        service = 'aoss'
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            self._parameters.region,
            service,
            session_token=credentials.token
        )
        opensearch_client = OpenSearch(
            hosts=[
                {
                    'host': self._parameters.index_host,
                    'port': 443
                }
            ],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=15
        )

        if self._knowledge_base_index_does_not_exists(opensearch_client, self._parameters.index_name):
            self._create_index(opensearch_client, self._parameters.index_name)

        self._load_knowledge_base_data(knowledge_base_data, opensearch_client, self._parameters.index_name)

    @classmethod
    def _knowledge_base_index_does_not_exists(cls, opensearch_client, index_name):
        index_does_not_exist = True

        existing_indices = opensearch_client.cat.indices()
        if index_name in existing_indices:
            index_does_not_exist = False

        return index_does_not_exist

    @classmethod
    def _load_knowledge_base_data(cls, json_data, opensearch_client, index_name):
        for json_object in json_data:
            opensearch_client.index(index=index_name, body=json_object)

    @classmethod
    def _create_index(cls, opensearch_client, index_name):
        LOGGER.debug('Creating index: %s', index_name)
        response = opensearch_client.indices.create(index_name)
        LOGGER.debug('Created index: %s', index_name)
        LOGGER.debug(response)
