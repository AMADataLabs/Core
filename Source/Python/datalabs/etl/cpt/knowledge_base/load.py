"""AWS OpenSearch Loader"""
from   dataclasses import dataclass
import json
import logging
import time

import boto3
from   opensearchpy import OpenSearch, RequestsHttpConnection
from   opensearchpy.helpers import bulk
from   requests_aws4auth import AWS4Auth

from   datalabs.etl.task import ETLException
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
    index_operation_delay: str = 30
    region: str = 'us-east-1'
    execution_time: str = None


class OpenSearchLoaderTask(Task):
    PARAMETER_CLASS = OpenSearchLoaderParameters

    def run(self):
        LOGGER.debug('Input data: \n%s', self._data)
        knowledge_base = json.loads(self._data[0].decode())
        index_operation_delay = int(self._parameters.index_operation_delay)
        opensearch = self._get_client(self._parameters.region, self._parameters.index_host, self._parameters.index_port)

        if self._index_exists(opensearch, self._parameters.index_name):
            self._delete_index(opensearch, self._parameters.index_name, index_operation_delay)

        self._create_index(opensearch, self._parameters.index_name, index_operation_delay)

        self._load_to_index(opensearch, self._parameters.index_name, knowledge_base)

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
        return opensearch.indices.exists(index=index_name)

    @classmethod
    def _delete_index(cls, opensearch, index_name, index_operation_delay):
        LOGGER.info("Deleting index %s", index_name)
        opensearch.indices.delete(index_name)

        LOGGER.info("Waiting %d seconds for delete to fully finish.", index_operation_delay)
        time.sleep(index_operation_delay)

    @classmethod
    def _create_index(cls, opensearch, index_name, index_operation_delay):
        LOGGER.info("Creating index %s", index_name)
        mappings = {
            "mappings": {
                "properties": {
                    "section": {"type": "keyword", "index": True},
                    "subsection": {"type": "keyword", "index": True},
                    "question": {"type": "text"},
                    "answer": {"type": "text"},
                    "updated_on": {"type": "date"},
                    "id": {"type": "integer"},
                    "article_id": {"type": "text"},
                }
            }
        }

        opensearch.indices.create(index_name, body=mappings)

        LOGGER.info("Waiting %d seconds for create to fully finish.", index_operation_delay)
        time.sleep(index_operation_delay)

    @classmethod
    def _load_to_index(cls, opensearch, index_name, knowledge_base):
        LOGGER.info("Loading index %s with %d documents.", index_name, len(knowledge_base))
        bulk_items = []

        for item in knowledge_base:
            bulk_items.append(cls._generate_bulk_item(index_name, item))

        updated_count, errors = bulk(opensearch, bulk_items, raise_on_error=False, raise_on_exception=False)

        LOGGER.debug("Bulk load results:\n%s", (updated_count, errors))

        if updated_count != len(bulk_items):
            raise ETLException(f"Failed to index {len(bulk_items) - updated_count} documents:\n{errors}")

    @classmethod
    def _generate_bulk_item(cls, index_name, item):
        document_id, document = cls._extract_document(item)

        return dict(
            _index=index_name,
            _id=document_id,
            _source=document
        )

    @classmethod
    def _load_document(cls, opensearch, index_name, item):
        document_id, document = cls._extract_document(item)

        response = opensearch.index(index=index_name, id=document_id, body=document)

        if response["result"] != "created":
            raise ETLException(f"Failed to index document {document_id}")

    @classmethod
    def _extract_document(cls, item):
        document_id = item.pop("document_id")

        return document_id, item
