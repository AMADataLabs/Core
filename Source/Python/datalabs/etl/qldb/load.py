"""AWS DynamoDB Loader"""
from   dataclasses import dataclass
import hashlib
from   itertools import chain
import json
import logging

from   pyqldb.config.retry_config import RetryConfig
from   pyqldb.driver.qldb_driver import QldbDriver

from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class QLDBLoaderParameters:
    primary_key: str
    ledger: str
    table: str
    execution_time: str = None


class QLDBLoaderTask(Task):
    PARAMETER_CLASS = QLDBLoaderParameters

    def run(self):
        LOGGER.debug('Input data: \n%s', self._data)
        LOGGER.info("Reading JSON data...")
        incoming_documents = self._add_hash_to_documents(json.loads(self._data[0]))
        current_hashes = self._get_current_hashes(incoming_documents)

        return [
            # json.dumps(self._delete_data(incoming_documents, current_hashes)).encode(),

            json.dumps(self._add_data(incoming_documents, current_hashes)).encode(),

            json.dumps(self._update_data(incoming_documents, current_hashes)).encode()
        ]

    def _get_qldb_client(self):
        retry_config = RetryConfig(retry_limit=3), json.loads(self._data[0])

        return QldbDriver(self._parameters.ledger, retry_config=retry_config[0])

    @classmethod
    def _add_hash_to_documents(cls, documents):
        return [cls._add_hash_to_document(document) for document in documents]

    def _get_current_hashes(self, incoming_documents):
        qldb = self._get_qldb_client()
        entity_ids = [doc["entityId"] for doc in incoming_documents]
        document_count = len(incoming_documents)
        end_indexes = chain(range(750, document_count, 750), [document_count])
        start_index = 0
        current_hashes = {}

        for end_index in end_indexes:
            LOGGER.info("Getting QLDB hashes (%d to %d of %d)...", start_index, end_index-1, document_count)
            batch = entity_ids[start_index:end_index]

            qldb.execute_lambda(lambda transaction_executor:
                self._get_current_hashes_from_qldb(transaction_executor, batch, current_hashes)
            )

            start_index = end_index

        return current_hashes

    def _delete_data(self, incoming_documents, current_hashes):
        deleted_primary_keys = self._get_deleted_primary_keys(incoming_documents, current_hashes)

        if deleted_primary_keys:
            self._delete_documents_from_qldb(deleted_primary_keys)

        return deleted_primary_keys

    def _add_data(self, incoming_documents, current_hashes):
        added_documents = self._get_added_data(incoming_documents, current_hashes)

        self._add_documents_to_qldb(added_documents)

        return added_documents

    def _update_data(self, incoming_documents, current_hashes):
        updated_documents = self._get_updated_documents(incoming_documents, current_hashes)

        self._update_documents_in_qldb(updated_documents)

        return updated_documents

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

    def _get_current_hashes_from_qldb(self, transaction_executor, entity_ids, current_hashes):
        entity_id_list = ",".join(entity_ids)
        cursor = transaction_executor.execute_statement(
            f"SELECT {self._parameters.primary_key}, md5 FROM {self._parameters.table} "
            f"WHERE entityId in ({entity_id_list})"
        )

        current_hashes.update({doc[self._parameters.primary_key]:doc.get('md5') for doc in cursor})

    def _delete_documents_from_qldb(self, deleted_primary_keys):
        qldb = self._get_qldb_client()
        document_count = len(deleted_primary_keys)
        end_indexes = chain(range(30, document_count, 30), [document_count])
        start_index = 0

        for end_index in end_indexes:
            LOGGER.info("Deleting QLDB records (%d to %d of %d)...", start_index, end_index-1, document_count)
            batch = deleted_primary_keys[start_index:end_index]
            placeholders = ", ".join("?" * len(batch))

            if batch:
                qldb.execute_lambda(lambda transaction_executor, placeholders=placeholders, batch=batch:
                    transaction_executor.execute_statement(
                        f"DELETE FROM {self._parameters.table} "
                        f"WHERE {self._parameters.table}.{self._parameters.primary_key} IN ({placeholders})",
                        *batch
                    )
                )

            start_index = end_index

    def _get_added_data(self, incoming_documents, current_hashes):
        current_primary_keys = list(current_hashes.keys())

        return [d for d in incoming_documents if d[self._parameters.primary_key] not in current_primary_keys]

    def _add_documents_to_qldb(self, added_documents):
        qldb = self._get_qldb_client()
        document_count = len(added_documents)
        end_indexes = chain(range(40, document_count, 40), [document_count])
        start_index = 0

        for end_index in end_indexes:
            LOGGER.info("Inserting QLDB records (%d to %d of %d)...", start_index, end_index-1, document_count)
            batch = added_documents[start_index:end_index]
            sql = "INSERT INTO " + self._parameters.table + " <<" + ", ".join(["?"] * len(batch)) + ">>"

            if batch:
                qldb.execute_lambda(lambda transaction_executor:
                    transaction_executor.execute_statement(
                        sql, *batch
                    )
                )

            start_index = end_index

    def _get_updated_documents(self, incoming_documents, current_hashes):
        current_primary_keys = list(current_hashes.keys())
        existing_documents = [d for d in incoming_documents if d[self._parameters.primary_key] in current_primary_keys]

        return [d for d in existing_documents if d["md5"] != current_hashes[d[self._parameters.primary_key]]]

    def _update_documents_in_qldb(self, updated_documents):
        LOGGER.info("Updating %d documents...", len(updated_documents))
        for index, document in enumerate(updated_documents):
            if index % 40 == 0:
                qldb = self._get_qldb_client()

            qldb.execute_lambda(lambda transaction_executor, document=document:
                transaction_executor.execute_statement(
                    f"UPDATE {self._parameters.table} AS p SET p = ? WHERE p. {self._parameters.primary_key} = ?",
                    document, document[self._parameters.primary_key]
                )
            )

    @classmethod
    def _sort_inner_keys_if_dict(cls, element):
        sorted_element = {key: cls._sort_inner_keys(value) for key, value in element.items()}
        return dict(sorted(sorted_element.items()))
