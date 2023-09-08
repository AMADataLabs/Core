"""AWS DynamoDB Loader"""
import json
import logging

from   dataclasses import dataclass
from   datalabs.access.aws import AWSClient
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class OpenSearchLoaderParameters:
    table: str = None
    execution_time: str = None
    index_name: str = None


class OpensearchLoaderTask(Task):
    PARAMETER_CLASS = OpenSearchLoaderParameters

    def run(self):
        LOGGER.debug('Input data: \n%s', self._data)
        knowledge_base_data = json.loads(self._data[0])

        with AWSClient("opensearch") as opensearch_client:
            if self._knowledge_base_index_does_not_exists(opensearch_client, self._parameters.index):
                self._create_index(opensearch_client, self._parameters.index)
            self._load_knowledge_base_data(knowledge_base_data, opensearch_client, self._parameters.index)

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
