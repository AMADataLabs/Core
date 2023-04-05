"""AWS DynamoDB Loader"""
import ast
from   bisect import bisect_left
from   collections import defaultdict
from   dataclasses import dataclass
import hashlib
import json
import logging
import re

import boto3
import pandas

from   datalabs.access.aws import AWSClient
from   datalabs.access.orm import Database
from   datalabs.task import Task
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class DynamoDBLoaderTask(Task):

    def run(self):
        # LOGGER.debug('Input data: \n%s', self._data)

        incoming_hashes = self._create_hash_entries(eval(self._data[0].decode('utf-8')))

        current_hashes = self._get_current_items()

        self._update(incoming_hashes, self._data[0], current_hashes)

    @classmethod
    def _create_hash_entries(cls, data):
        incoming_hashes = []

        for item in data:
            if item["sk"].startswith("UNMAPPABLE:") or item["sk"].startswith("CPT:"):
                md5 = hashlib.md5(json.dumps(item, sort_keys=True).encode('utf-8')).hexdigest()
                incoming_hashes.append(dict(pk=item["pk"], sk=f"MD5:{md5}"))

        return incoming_hashes

    def _get_current_items(self):
        with AWSClient("dynamodb") as db:
            items = self._query_table(db, self._parameters.get('TABLE'))

        return items

    def _query_table(self, db, table):
        items = []
        results = db.execute_statement(
            Statement=f"SELECT * FROM \"{table}\".\"SearchIndex\" WHERE begins_with(\"sk\", 'MD5:')",
        )
        items.extend(results['Items'])

        if self._check_for_token(results):
            items = self._query_table_with_token(db, items, results['NextToken'], table)

        return items

    @classmethod
    def _check_for_token(cls, results):
        if 'NextToken' in results:
            token_exists = True
        else:
            token_exists = False

        return token_exists

    @classmethod
    def _query_table_with_token(cls, db, items, token, table):
        results = db.execute_statement(
            Statement=f"SELECT * FROM \"{table}\".\"SearchIndex\" WHERE begins_with(\"sk\", 'MD5:')",
            NextToken=token
        )
        items.extend(results['Items'])

        if cls._check_for_token(results):
            cls._query_table_with_token(db, items, results['NextToken'], table)

        return items

    def _update(self, incoming_hashes, incoming_data, current_hashes):
        self._delete_data(incoming_hashes, incoming_data, current_hashes)

        self._update_data(incoming_hashes, current_hashes)

        self._add_data(incoming_hashes, current_hashes)

    def _delete_data(self, incoming_hashes, incoming_data, current_hashes):
        deleted_data = self._select_deleted_data(incoming_hashes, incoming_data, current_hashes)

        self._delete_data_from_table(deleted_data)

    @classmethod
    def _select_deleted_data(cls, incoming_hashes, incoming_data, current_hashes):
        deleted_data = [old_hash for old_hash in current_hashes
                        if not any(old_hash['sk'] == new_hash['sk'] and old_hash['pk'] == new_hash['pk']
                                   for new_hash in incoming_hashes)
                        ]
        import pdb
        pdb.set_trace()

        LOGGER.debug('Deleted Data: %s', deleted_data)

        return deleted_data

# MD5 entries are not directly mappable back to a mapping (they only identify the concept).
# A mapping is either new or changed if the calculated MD5 is not in the list of MD5s for that concept.
# To distinguish between new or changed, attempt to pull the (sk, pk) where sk == “CPT:<CPT Code>”.
# If it exists, the mapping has been updated.
