"""AWS DynamoDB Loader"""
from   collections import defaultdict
from   dataclasses import dataclass
import hashlib
import json
import logging

import pandas

from   datalabs.access.aws import AWSClient, AWSResource
from   datalabs.parameter import add_schema
from   datalabs.task import Task

from pyqldb.config.retry_config import RetryConfig
from pyqldb.driver.qldb_driver import QldbDriver

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class QLDBLoaderParameters:
    primary_key: str
    ledger: str
    table: str = None
    execution_time: str = None


class QLDBLoaderTask(Task):
    PARAMETER_CLASS = QLDBLoaderParameters

    def run(self):
        LOGGER.debug('Input data: \n%s', self._data)
        raw_documents = json.loads(self._data[0])

        retry_config = RetryConfig(retry_limit=3)
        qldb_driver = QldbDriver(self._parameters.ledger, retry_config=retry_config)

        incoming_documents = self._add_hash_to_entries(raw_documents)
        current_hashes_and_entity_ids = qldb_driver.execute_lambda(lambda executor: self._get_current_hashes_and_entity_ids(executor))

        qldb_driver.execute_lambda(lambda executor: self._delete_data(executor, incoming_documents, current_hashes_and_entity_ids))
        qldb_driver.execute_lambda(lambda executor: self._add_data(executor, incoming_documents, current_hashes_and_entity_ids))
        qldb_driver.execute_lambda(lambda executor: self._update_data(executor, incoming_documents, current_hashes_and_entity_ids))

    @classmethod
    def _add_hash_to_entries(cls, documents):
        hashed_documents = []

        for document in documents:
            document = cls._sort_inner_keys(document)
            document["md5"] = hashlib.md5(json.dumps(document, sort_keys=True).encode('utf-8')).hexdigest()
            hashed_documents.append(document)

        return hashed_documents

    def _get_current_hashes_and_entity_ids(self, transaction_executor):
        cursor = transaction_executor.execute_statement("SELECT " + self._parameters.primary_key + ", md5 from loader_development")

        current_hashes_and_entity_ids = {}

        for doc in cursor:
            current_hashes_and_entity_ids[doc[self._parameters.primary_key]] = doc['md5']

        return current_hashes_and_entity_ids

    def _delete_data(self, transaction_executor, incoming_documents, current_hashes_and_entity_ids):
        for entity_id in current_hashes_and_entity_ids:
            delete_document = True
            for document in incoming_documents:
                if document[self._parameters.primary_key] == entity_id:
                    delete_document = False

            if delete_document:
                transaction_executor.execute_statement("DELETE FROM loader_development WHERE loader_development." + self._parameters.primary_key + " = ?", entity_id)

    def _add_data(self, transaction_executor, incoming_documents, current_hashes_and_entity_ids):
        for document in incoming_documents:
            if document[self._parameters.primary_key] not in current_hashes_and_entity_ids.keys():
                transaction_executor.execute_statement("INSERT INTO loader_development ?", document)

    def _update_data(self, transaction_executor, incoming_documents, current_hashes_and_entity_ids):
        for entity_id in current_hashes_and_entity_ids:
            for document in incoming_documents:
                if document[self._parameters.primary_key] == entity_id and document['md5'] != current_hashes_and_entity_ids[entity_id]:
                    transaction_executor.execute_statement("UPDATE loader_development AS p SET p = ? WHERE p." + self._parameters.primary_key + " = ?", document, entity_id)

    @classmethod
    def _sort_inner_keys(cls, obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                obj[key] = cls._sort_inner_keys(value)
            return dict(sorted(obj.items()))
        elif isinstance(obj, list):
            return [cls._sort_inner_keys(item) for item in obj]
        else:
            return obj