"""AWS DynamoDB Loader"""
import json
import logging
from dataclasses import dataclass

from datalabs.access.aws import AWSClient
from datalabs.parameter import add_schema
from datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class OpensearchLoaderParameters:
    table: str = None
    execution_time: str = None
    index_name: str = None


class OpensearchLoaderTask(Task):
    PARAMETER_CLASS = OpensearchLoaderParameters

    def run(self):
        LOGGER.debug('Input data: \n%s', self._data)
        json_data = json.loads(self._data[0])
        with AWSClient("opensearch") as opensearch_client:
            if self._knowledge_base_index_does_not_exists(opensearch_client, 'knowledge-base'):
                self._create_index(opensearch_client, 'knowledge_base')
            self._load_knowledge_base_data(json_data, opensearch_client)

    @classmethod
    def _knowledge_base_index_does_not_exists(cls, opensearch_client, index_name):
        existing_indices = opensearch_client.cat.indices()
        if index_name in existing_indices:
            return False
        return True

    @classmethod
    def _load_knowledge_base_data(cls, json_data, opensearch_client):
        for json_object in json_data:
            opensearch_client.index(
                index='knowledge-base',
                body=json_object
            )

    @classmethod
    def _create_index(cls, opensearch_client, index_name):
        try:
            LOGGER.debug('Creating index: {name}')
            response = opensearch_client.indices.create(index_name)
            LOGGER.debug('Created index: {name}')
            LOGGER.debug(response)
        except Exception as exp:
            LOGGER.debug(f"exp Creating index {index_name}: {exp}")
