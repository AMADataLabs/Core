"""AWS DynamoDB Loader"""
import hashlib
import json
import logging

import pandas

from   dataclasses import dataclass
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

        # if self._parameters.append is None or self._parameters.append.upper() != 'TRUE':
        #     self._delete_data(incoming_hashes, current_hashes)

        self._add_data(incoming_hashes, current_hashes)


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
                f"SELECT sk, pk, md5 FROM \"{self._parameters.table}\" WHERE sk = 'CONCEPT:' AND pk = 'CPT CODE:'"
            )

            current_hashes_rows = [(x["sk"]["S"], x["pk"]["S"], x["md5"]["S"]) for x in results]

        current_hashes = pandas.DataFrame(current_hashes_rows, columns=["sk", "pk", "md5"])

        return current_hashes

    def _add_data(self, incoming_hashes, current_hashes):
        new_hashes = self._select_new_hashes(incoming_hashes, current_hashes)
        new_hashes_table = [new_hashes[hash_pk] for hash_pk in new_hashes]

        self._add_to_table(new_hashes_table)

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
