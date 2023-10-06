"""AWS DynamoDB Loader"""
from   dataclasses import dataclass
import hashlib
import json
import logging

import pandas

from   datalabs.access.aws import AWSClient, AWSResource
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DynamoDBLoaderParameters:
    table: str = None
    execution_time: str = None
    append: str = None


class DynamoDBLoaderTask(Task):
    PARAMETER_CLASS = DynamoDBLoaderParameters

    def run(self):
        LOGGER.debug('Input data: \n%s', self._data)
        incoming_mappings = json.loads(self._data[0])

        incoming_hashes = self._create_hash_entries(incoming_mappings)
        LOGGER.debug("Incoming Hashes:\n%s", incoming_hashes)

        current_hashes = self._get_current_hashes()
        LOGGER.debug("Current Hashes:\n%s", current_hashes)

        if self._parameters.append is None or self._parameters.append.upper() != 'TRUE':
            self._delete_data(incoming_hashes, current_hashes)

        self._add_data(incoming_hashes, current_hashes)

        self._update_data(incoming_hashes, current_hashes)


    @classmethod
    def _create_hash_entries(cls, data):
        incoming_hashes = []
        hash_entries = pandas.DataFrame()

        for item in data:
            md5 = hashlib.md5(json.dumps(item, sort_keys=True).encode('utf-8')).hexdigest()
            item['md5'] = md5
            incoming_hashes.append(item)

        if incoming_hashes:
            hash_entries = pandas.DataFrame(incoming_hashes)

        return hash_entries

    def _get_current_hashes(self):
        current_hashes_rows = []

        with AWSClient("dynamodb") as dynamodb:
            results = self._paginate(
                dynamodb,
                f"SELECT sk, pk, md5 FROM \"{self._parameters.table}\""
            )

            current_hashes_rows = [(x["sk"]["S"], x["pk"]["S"], x["md5"]["S"]) for x in results]

        current_hashes = pandas.DataFrame(current_hashes_rows, columns=["sk", "pk", "md5"])

        return current_hashes

    def _delete_data(self, incoming_hashes, current_hashes):
        deleted_hashes = self._select_deleted_hashes(incoming_hashes, current_hashes)

        if len(deleted_hashes) > 0:
            self._delete_from_table(deleted_hashes)

    def _add_data(self, incoming_hashes, current_hashes):
        new_hashes = self._select_new_hashes(incoming_hashes, current_hashes)
        new_hashes_table = [new_hashes[hash_pk] for hash_pk in new_hashes]

        self._add_to_table(new_hashes_table)

    def _update_data(self, incoming_hashes, current_hashes):
        updated_hashes = self._select_updated_hashes(incoming_hashes, current_hashes)
        old_hashes = self._get_old_hashes(updated_hashes, current_hashes)

        if len(updated_hashes) > 0:
            self._replace_in_table(old_hashes, updated_hashes)

    @classmethod
    def _select_deleted_hashes(cls, incoming_hashes, current_hashes):
        deleted_hashes = current_hashes[~current_hashes.pk.isin(incoming_hashes.pk)].reset_index(drop=True)

        LOGGER.debug('Deleted Data: %s', deleted_hashes)

        return deleted_hashes.to_dict(orient='records')

    def _delete_from_table(self, data):
        with self._get_table().batch_writer() as batch:
            for item in data:
                batch.delete_item(Key={
                    'pk': item['pk'],
                    'sk': item['sk']
                })
                LOGGER.debug('Deleted Item: %s', item['pk'])

    @classmethod
    def _select_new_hashes(cls, incoming_hashes, current_hashes):
        new_or_updated_hashes = incoming_hashes[~incoming_hashes.sk.isin(current_hashes.sk)].reset_index(drop=True)

        new_hashes = new_or_updated_hashes[~new_or_updated_hashes.pk.isin(current_hashes.pk)].reset_index(drop=True)

        LOGGER.debug('New Hashes: %s', new_hashes)

        return {hash["pk"]: hash for hash in new_hashes.to_dict(orient='records')}

    def _add_to_table(self, data):
        with self._get_table().batch_writer() as batch:
            for item in data:
                LOGGER.debug('Adding item: %s', item['pk'])
                batch.put_item(Item=item)
                LOGGER.debug('Added Item: %s', item['pk'])

    @classmethod
    def _select_updated_hashes(cls, incoming_hashes, current_hashes):
        new_or_updated_hashes = incoming_hashes[~incoming_hashes.md5.isin(current_hashes.md5)]

        updated_hashes = new_or_updated_hashes[new_or_updated_hashes.pk.isin(current_hashes.pk)]

        LOGGER.debug('Updated Data: %s', updated_hashes)

        return updated_hashes.to_dict(orient='records')

    @classmethod
    def _get_old_hashes(cls, updated_hashes, current_hashes):
        current_hashes = current_hashes.to_dict(orient='records')
        old_hashes = []

        for updated_hash in updated_hashes:
            for current_hash in current_hashes:
                if current_hash['pk'] == updated_hash['pk']:
                    old_hashes.append(current_hash)

        return old_hashes

    def _replace_in_table(self, old_data, new_data):
        self._delete_from_table(old_data)

        self._add_to_table(new_data)

    def _get_table(self):
        ''' Get a DyanmoDB table object. Since the boto3 client does not hold a connection open, we can
            use the AWSResource context manager to create a table object and return without any ill effects.
        '''
        table = None

        with AWSResource("dynamodb") as resource:
            table = resource.Table(self._parameters.table)

        return table

    @classmethod
    def _paginate(cls, dynamodb, statement):
        results = dynamodb.execute_statement(Statement=statement)

        for item in results["Items"]:
            yield item

        while "NextToken" in results:
            results = dynamodb.execute_statement(Statement=statement, NextToken=results["NextToken"])

            for item in results["Items"]:
                yield item
