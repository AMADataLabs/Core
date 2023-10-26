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
    index_port: str = 443
    region: str = 'us-east-1'
    execution_time: str = None


class OpenSearchLoaderTask(Task):
    PARAMETER_CLASS = OpenSearchLoaderParameters

    def run(self):
        LOGGER.debug('Input data: \n%s', self._data)
        knowledge_base = json.loads(self._data[0].decode())
        opensearch = self._get_client(self._parameters.region, self._parameters.host, self._parameters.port)

        if not self._index_exists(opensearch, self._parameters.index_name):
            self._create_index(opensearch, self._parameters.index_name)

        self._load_index(opensearch, self._parameters.index_name, knowledge_base)

    @classmethod
    def _get_client(cls, region, host, port):
        port = int(port)
        service = "aoss"
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            region,
            service,
            session_token=credentials.token,
        )

        return OpenSearch(
            hosts=[{"host": host, "port": port}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=15,
        )

    @classmethod
    def _index_exists(cls, opensearch, index_name):
        index_exists = False

        existing_indices = opensearch.cat.indices()

        if index_name in existing_indices:
            index_exists = True

        return index_exists

    @classmethod
    def _create_index(cls, opensearch, index_name):
        LOGGER.debug('Creating index: %s', index_name)
        response = opensearch.indices.create(index_name)
        LOGGER.debug('Created index: %s', index_name)
        LOGGER.debug(response)

    @classmethod
    def _load_index(cls, opensearch, index_name, json_data):
        for json_object in json_data:
            opensearch.index(index=index_name, body=json_object)
