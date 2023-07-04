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

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DynamoDBLoaderParameters:
    table: str = None
    execution_time: str = None


class DynamoDBLoaderTask(Task):
    PARAMETER_CLASS = DynamoDBLoaderParameters

    def run(self):
        LOGGER.debug('Input data: \n%s', self._data)
        incoming_mappings = json.loads(self._data[0])

        incoming_hashes = self._create_hash_entries(incoming_mappings)

        current_hashes = self._get_current_hashes()

        self._delete_data(incoming_hashes, current_hashes)

        self._add_data(incoming_hashes, current_hashes, incoming_mappings)

        self._update_data(incoming_hashes, current_hashes, incoming_mappings)

    @classmethod
    def _create_hash_entries(cls, data):
        incoming_hashes = []

        for item in data:
            if item["sk"].startswith("UNMAPPABLE:") or item["sk"].startswith("CPT:"):
                md5 = hashlib.md5(json.dumps(item, sort_keys=True).encode('utf-8')).hexdigest()

                incoming_hashes.append(dict(pk=f'{item["pk"]}:{item["sk"]}', sk=f"MD5:{md5}"))

        return pandas.DataFrame(incoming_hashes)

    def _get_current_hashes(self):
        current_hashes_columns = defaultdict(list)

        with AWSClient("dynamodb") as dynamodb:
            results = self._paginate(
                dynamodb,
                f"SELECT * FROM \"{self._parameters.table}\".\"SearchIndex\" WHERE begins_with(\"sk\", 'MD5:')"
            )

            for result in results:
                for key, value in result.items():
                    current_hashes_columns[key].append(value["S"])

        current_hashes = pandas.DataFrame(current_hashes_columns)

        return current_hashes

    def _delete_data(self, incoming_hashes, current_hashes):
        deleted_hashes = self._select_deleted_hashes(incoming_hashes, current_hashes)
        deleted_mappings = self._get_deleted_mappings(deleted_hashes)
        deleted_keywords = self._get_deleted_keywords(deleted_hashes)

        if len(deleted_hashes) > 0:
            self._delete_from_table(deleted_mappings)

            self._delete_from_table(deleted_keywords)

            self._delete_from_table(deleted_hashes)

    def _add_data(self, incoming_hashes, current_hashes, incoming_mappings):
        new_hashes = self._select_new_hashes(incoming_hashes, current_hashes)
        new_mappings = self._get_new_mappings(new_hashes, incoming_mappings)
        new_keywords = self._get_new_keywords(new_hashes, incoming_mappings)

        if len(new_hashes) > 0:
            self._add_to_table(new_mappings)

            self._add_to_table(new_keywords)

            self._add_to_table(new_hashes)

    def _update_data(self, incoming_hashes, current_hashes, incoming_mappings):
        updated_hashes = self._select_updated_hashes(incoming_hashes, current_hashes)
        updated_mappings = self._get_updated_mappings(updated_hashes, incoming_mappings)
        updated_keywords = self._get_updated_keywords(updated_hashes, incoming_mappings)
        old_keywords = self._get_old_keywords(updated_hashes)
        old_hashes = self._get_old_hashes(updated_hashes, current_hashes)

        if len(updated_hashes) > 0:
            self._update_mappings_in_table(updated_mappings)

            self._replace_in_table(old_keywords, updated_keywords)

            self._replace_in_table(old_hashes, updated_hashes)

    @classmethod
    def _select_deleted_hashes(cls, incoming_hashes, current_hashes):
        deleted_hashes = current_hashes[~current_hashes.pk.isin(incoming_hashes.pk)].reset_index(drop=True)

        LOGGER.debug('Deleted Data: %s', deleted_hashes)

        return deleted_hashes.to_dict(orient='records')

    @classmethod
    def _get_deleted_mappings(cls, deleted_hashes):
        deleted_mappings = []

        for item in deleted_hashes:
            deleted_mappings.append({
                'pk': item['pk'].rsplit(':', 2)[0],
                'sk': item['pk'].split(':', 2)[2]
            })

        return deleted_mappings

    def _get_deleted_keywords(self, deleted_hashes):
        table = self._parameters.table
        keyword_data = []

        with AWSClient("dynamodb") as dynamodb:
            for item in deleted_hashes:
                results = self._paginate(
                    dynamodb,
                    f"SELECT * FROM \"{table}\" WHERE pk='{item['pk']}' and begins_with(\"sk\", 'KEYWORD:')"
                )
                keyword_data.extend(list(results))

        return [dict(pk=item['pk']['S'], sk=item['sk']['S']) for item in keyword_data]

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

        LOGGER.debug('Added Data: %s', new_hashes)

        return new_hashes.to_dict(orient='records')

    @classmethod
    def _get_new_mappings(cls, new_hashes, incoming_mappings):
        incoming_mappings_lookup_table = {':'.join((m["pk"], m["sk"])):m for m in incoming_mappings}

        return [incoming_mappings_lookup_table[hash_item["pk"]] for hash_item in new_hashes]

    @classmethod
    def _get_new_keywords(cls, new_hashes, incoming_mappings):
        keywords = []

        for item in new_hashes:
            for data in incoming_mappings:
                if item["pk"] == data['pk']:
                    keywords.append(data)

        return keywords

    def _add_to_table(self, data):
        with self._get_table().batch_writer() as batch:
            for item in data:
                batch.put_item(Item=item)
                LOGGER.debug('Added Item: %s', item['pk'])

    @classmethod
    def _select_updated_hashes(cls, incoming_hashes, current_hashes):
        new_or_updated_hashes = incoming_hashes[~incoming_hashes.sk.isin(current_hashes.sk)]

        updated_hashes = new_or_updated_hashes[new_or_updated_hashes.pk.isin(current_hashes.pk)]

        LOGGER.debug('Updated Data: %s', updated_hashes)

        return updated_hashes.to_dict(orient='records')

    @classmethod
    def _get_updated_mappings(cls, updated_hashes, incoming_mappings):
        incoming_mappings_lookup_table = {':'.join((m["pk"], m["sk"])):m for m in incoming_mappings}

        return [incoming_mappings_lookup_table[hash_item["pk"]] for hash_item in updated_hashes]

    @classmethod
    def _get_updated_keywords(cls, updated_hashes, incoming_mappings):
        incoming_keywords = []

        for hash_item in updated_hashes:
            for data in incoming_mappings:
                if hash_item['pk'] == data['pk']:
                    incoming_keywords.append(data)

        return incoming_keywords

    def _get_old_keywords(self, updated_hashes):
        table = self._parameters.table
        updated_old_keywords = []

        with AWSClient("dynamodb") as dynamodb:
            for item in updated_hashes:
                results = self._paginate(
                    dynamodb,
                    f"SELECT * FROM \"{table}\" WHERE pk='{item['pk']}' and begins_with(\"sk\", 'KEYWORD:')"
                )
                updated_old_keywords.extend(list(results))

        return updated_old_keywords

    @classmethod
    def _get_old_hashes(cls, updated_hashes, current_hashes):
        current_hashes = current_hashes.to_dict(orient='records')
        old_hashes = []

        for updated_hash in updated_hashes:
            for current_hash in current_hashes:
                if current_hash['pk'] == updated_hash['pk']:
                    old_hashes.append(current_hash)

        return old_hashes

    def _update_mappings_in_table(self, mappings):
        for mapping in mappings:
            self._get_table().update_item(
                Key={
                    'pk': mapping['pk'],
                    'sk': mapping['sk']
                },
                UpdateExpression='SET snomed_descriptor=:s, map_category=:m, cpt_descriptor=:c',
                ExpressionAttributeValues={
                    ':s': mapping['snomed_descriptor'],
                    ':m': mapping['map_category'],
                    ':c': mapping['cpt_descriptor']
                }
            )
            LOGGER.debug('Updated Mapping: %s', mapping['pk'])

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
