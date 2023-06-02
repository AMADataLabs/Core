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
        qldb = self._get_qldb_client()
        incoming_documents = self._add_hash_to_documents(json.loads(self._data[0]))
        current_hashes = qldb.execute_lambda(lambda executor: self._get_current_hashes(executor))

        qldb.execute_lambda(lambda executor: self._delete_data(executor, incoming_documents, current_hashes))

        qldb.execute_lambda(lambda executor: self._add_data(executor, incoming_documents, current_hashes))

        qldb.execute_lambda(lambda executor: self._update_data(executor, incoming_documents, current_hashes))

    def _get_qldb_client(self):
        retry_config = RetryConfig(retry_limit=3), json.loads(self._data[0])
        return QldbDriver(self._parameters.ledger, retry_config=retry_config[0])

    @classmethod
    def _add_hash_to_documents(cls, documents):
        return [cls._add_hash_to_document(document) for document in documents]

    def _get_current_hashes(self, transaction_executor):
        cursor = transaction_executor.execute_statement("SELECT " + self._parameters.primary_key + ", md5 from " + self._parameters.table)
        current_hashes = {}

        return {doc[self._parameters.primary_key]:doc['md5'] for doc in cursor}

    def _delete_data(self, transaction_executor, incoming_documents, current_hashes):
        deleted_primary_keys = self._get_deleted_primary_keys(incoming_documents, current_hashes)

        self._delete_documents_from_qldb(deleted_primary_keys, transaction_executor)

    def _add_data(self, transaction_executor, incoming_documents, current_hashes):
        added_documents = self._get_added_data(incoming_documents, current_hashes)

        self._add_documents_to_qldb(added_documents, transaction_executor)

    def _update_data(self, transaction_executor, incoming_documents, current_hashes):
        updated_documents = self._get_updated_documents(incoming_documents, current_hashes)

        self._update_documents_in_qldb(updated_documents, transaction_executor)

    @classmethod
    def _add_hash_to_document(cls, document):
        document = cls._sort_inner_keys(document)
        document["md5"] = hashlib.md5(json.dumps(document, sort_keys=True).encode('utf-8')).hexdigest()
        return document

    @classmethod
    def _sort_inner_keys(cls, element):
        sorted_element = None

        if isinstance(element, dict):
            sorted_element = cls._sort_inner_keys_if_dict(element)
        elif isinstance(element, list):
            sorted_element = [cls._sort_inner_keys(item) for item in element]
        else:
            sorted_element = element

        return sorted_element

    def _get_deleted_primary_keys(self, incoming_documents, current_hashes):
        incoming_primary_keys = [d[self._parameters.primary_key] for d in incoming_documents]

        return [key for key in current_hashes.keys() if key not in incoming_primary_keys]

    def _delete_documents_from_qldb(self, deleted_primary_keys, transaction_executor):
        for key in deleted_primary_keys:
            transaction_executor.execute_statement("DELETE FROM " + self._parameters.table + " WHERE " + self._parameters.table + "." + self._parameters.primary_key + " = ?", key)

    def _get_added_data(self, incoming_documents, current_hashes):
        current_primary_keys = list(current_hashes.keys())

        return [d for d in incoming_documents if d[self._parameters.primary_key] not in current_primary_keys]

    def _add_documents_to_qldb(self, added_documents, transaction_executor):
        for document in added_documents:
            transaction_executor.execute_statement("INSERT INTO " + self._parameters.table + " ?", document)

    def _get_updated_documents(self, incoming_documents, current_hashes):
        current_primary_keys = list(current_hashes.keys())
        existing_documents = [d for d in incoming_documents if d[self._parameters.primary_key] in current_primary_keys]

        return [d for d in existing_documents if d["md5"] != current_hashes[d[self._parameters.primary_key]]]

    def _update_documents_in_qldb(self, updated_documents, transaction_executor):
        for document in updated_documents:
            transaction_executor.execute_statement("UPDATE " + self._parameters.table + " AS p SET p = ? WHERE p." + self._parameters.primary_key + " = ?", document, document[self._parameters.primary_key])

    @classmethod
    def _sort_inner_keys_if_dict(cls, element):
        sorted_element = {key: cls._sort_inner_keys(value) for key, value in element.items()}
        return dict(sorted(sorted_element.items()))