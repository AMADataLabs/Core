"""AWS DynamoDB Loader"""
import hashlib
import json
import logging

import boto3
import pandas

from   datalabs.access.aws import AWSClient
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class DynamoDBLoaderTask(Task):
    def run(self):
        # LOGGER.debug('Input data: \n%s', self._data)

        incoming_hashes = self._create_hash_entries(eval(self._data[0].decode('utf-8')))

        with AWSClient("dynamodb") as client:
            current_hashes = self._get_current_hashes(client)

        with AWSClient("dynamodb").resource as resource:
            table = resource.Table("CPT-API-snomed-sbx")

            self._delete_data(incoming_hashes, current_hashes, table)

            self._add_data(incoming_hashes, current_hashes, table, self._data[0].decode('utf-8'))

            self._update_data(incoming_hashes, current_hashes)

    @classmethod
    def _create_hash_entries(cls, data):
        incoming_hashes = []

        for item in data:
            if item["sk"].startswith("UNMAPPABLE:") or item["sk"].startswith("CPT:"):
                md5 = hashlib.md5(json.dumps(item, sort_keys=True).encode('utf-8')).hexdigest()
                incoming_hashes.append({'pk': {'S': f'{item["pk"]}:{item["sk"]}'}, 'sk': {'S': f"MD5:{md5}"}})

        return incoming_hashes

    def _get_current_hashes(self, database):
        items = self._query_table(database, self._parameters.get('TABLE'))

        return items

    def _query_table(self, database, table):
        items = []

        results = database.execute_statement(
            Statement=f"SELECT * FROM \"{table}\".\"SearchIndex\" WHERE begins_with(\"sk\", 'MD5:')",
        )
        items.extend(results['Items'])

        if self._check_for_token(results):
            items = self._query_table_with_token(database, items, results['NextToken'], table)

        return items

    @classmethod
    def _check_for_token(cls, results):
        if 'NextToken' in results:
            token_exists = True
        else:
            token_exists = False

        return token_exists

    @classmethod
    def _query_table_with_token(cls, database, items, token, table):
        results = database.execute_statement(
            Statement=f"SELECT * FROM \"{table}\".\"SearchIndex\" WHERE begins_with(\"sk\", 'MD5:')",
            NextToken=token
        )
        items.extend(results['Items'])

        if cls._check_for_token(results):
            cls._query_table_with_token(database, items, results['NextToken'], table)

        return items

    def _delete_data(self, incoming_hashes, current_hashes, table):
        deleted_data = self._select_deleted_data(incoming_hashes, current_hashes)

        self._delete_data_from_table(deleted_data, table)

    @classmethod
    def _select_deleted_data(cls, incoming_hashes, current_hashes):
        import pdb
        pdb.set_trace()
        incoming_hashes = pandas.DataFrame(incoming_hashes)

        current_hashes = pandas.DataFrame(current_hashes)

        deleted_data = current_hashes[~current_hashes['pk'].isin(incoming_hashes['pk'])]

        LOGGER.debug('Deleted Data: %s', deleted_data)

        return deleted_data.to_dict(orient='records')

    def _delete_data_from_table(self, deleted_data, table):
        if len(deleted_data) > 0:
            self._delete_hashes_from_table(deleted_data, table)

            self._delete_mappings_from_table(deleted_data, table)

    @classmethod
    def _delete_hashes_from_table(cls, deleted_data, table):
        with table.batch_writer() as batch:
            for item in deleted_data:
                LOGGER.debug("Item %s", item)
                batch.delete_item(Key={'pk': item["pk"],
                                       'sk': item["sk"]})

    @classmethod
    def _delete_mappings_from_table(cls, deleted_data, database):
        with database.batch_writer() as batch:
            for item in deleted_data:
                batch.delete_item(Key={'pk': item['pk']['S'].rsplit(":", 2)[0],
                                       'sk': item['pk']['S'].split(":", 2)[2]})

    def _add_data(self, incoming_hashes, current_hashes, database, incoming_data):
        new_data = self._select_new_data(incoming_hashes, current_hashes)

        self._add_data_to_table(new_data, database, incoming_data)

    @classmethod
    def _select_new_data(cls, incoming_hashes, current_hashes):
        incoming_hashes = pandas.DataFrame(incoming_hashes, columns=['pk', 'sk'])

        current_hashes = pandas.DataFrame(current_hashes, columns=['pk', 'sk'])
        current_hashes = current_hashes[pandas.isnull(current_hashes['ref'])].drop(['ref'], axis=1).reset_index()

        new_data = incoming_hashes[~incoming_hashes['pk'].isin(current_hashes['pk'])]

        LOGGER.debug('Added Data: %s', new_data)

        return new_data.to_dict(orient='records')

    def _add_data_to_table(self, new_data, database, incoming_data):
        if len(new_data) > 0:
            self._add_hashes_to_table(new_data, database)

            self._add_mappings_to_table(new_data, database, incoming_data)

    def _add_hashes_to_table(self, new_data, database):
        with database.batch_writer() as batch:
            for item in new_data:
                batch.put_item(TableName=self._parameters.get('TABLE'),
                               Item=item)

    def _add_mappings_to_table(self, new_data, database, incoming_data):
        self._add_cpt_mapping(new_data, database, incoming_data)

        self._add_keyword_mapping(new_data, database, incoming_data)

    def _add_cpt_mapping(self, new_data, database, incoming_data):
        with database.batch_writer() as batch:
            for items in new_data:
                for item in incoming_data:
                    if item["pk"] == items['pk']['S'].rsplit(":", 2)[0] and item["sk"] == item['pk']['S'].split(":", 2)[2]:
                        batch.put_item(TableName=self._parameters.get('TABLE'),
                                       Item=item)

    def _add_keyword_mapping(self, new_data, database, incoming_data):
        with database.batch_writer() as batch:
            for items in new_data:
                for item in incoming_data:
                    if item["pk"] == items['pk']['S']:
                        batch.put_item(TableName=self._parameters.get('TABLE'),
                                       Item=item)
