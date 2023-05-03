"""AWS DynamoDB Loader"""
import hashlib
import json
import logging
from collections import defaultdict

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

        with AWSClient("dynamodb") as dynamodb:
            current_hashes = self._get_current_hashes(dynamodb)

            with AWSClient("dynamodb").resource as resource:
                table = resource.Table("CPT-API-snomed-sbx")

                self._delete_data(incoming_hashes, current_hashes, table, dynamodb)

                self._add_data(incoming_hashes, current_hashes, table, eval(self._data[0].decode('utf-8')))

                self._update_data(incoming_hashes, current_hashes, table, eval(self._data[0].decode('utf-8')), dynamodb)

    @classmethod
    def _create_hash_entries(cls, data):
        incoming_hashes = []

        for item in data:
            if item["sk"].startswith("UNMAPPABLE:") or item["sk"].startswith("CPT:"):
                md5 = hashlib.md5(json.dumps(item, sort_keys=True).encode('utf-8')).hexdigest()
                incoming_hashes.append(dict(pk=f'{item["pk"]}:{item["sk"]}', sk=f"MD5:{md5}"))

        return pandas.DataFrame(incoming_hashes)

    def _get_current_hashes(self, dynamodb):
        current_hashes_columns = defaultdict(list)

        results = self._paginate(dynamodb, "SELECT * FROM \"CPT-API-snomed-sbx\".\"SearchIndex\" WHERE begins_with(\"sk\", 'MD5:')")
        results = list(results)

        for result in results:
            for key, value in result.items():
                current_hashes_columns[key].append(value["S"])

        current_hashes = pandas.DataFrame(current_hashes_columns)

        return current_hashes

    def _delete_data(self, incoming_hashes, current_hashes, table, dynamodb):
        deleted_hashes = self._select_deleted_hashes(incoming_hashes, current_hashes)

        if len(deleted_hashes) > 0:
            self._delete_keywords_from_table(deleted_hashes, table, dynamodb)

            self._delete_cpt_mappings_from_table(deleted_hashes, table)

            self._delete_hashes_from_table(deleted_hashes, table)

    def _add_data(self, incoming_hashes, current_hashes, table, incoming_data):
        new_data = self._select_new_hashes(incoming_hashes, current_hashes)

        if len(new_data) > 0:
            self._add_keywords_to_table(new_data, table, incoming_data)

            self._add_cpt_mappings_to_table(new_data, table, incoming_data)

            self._add_hashes_to_table(new_data, table)

    def _update_data(self, incoming_hashes, current_hashes, table, incoming_data, dynamodb):
        updated_hashes = self._select_updated_hashes(incoming_hashes, current_hashes)

        if len(updated_hashes) > 0:
            updated_old_hashes = self._get_updated_old_hashes(updated_hashes, current_hashes)
            self._replace_in_table(updated_old_hashes, updated_hashes, table)

            updated_old_keywords = self._get_old_keywords(updated_hashes, dynamodb)
            updated_new_keywords = self._get_updated_keywords(updated_hashes, incoming_data)

            self._replace_in_table(updated_old_keywords, updated_new_keywords)

            self._update_cpt_mappings_in_table(updated_hashes, table, incoming_data)

    @classmethod
    def _paginate(cls, dynamodb, statement):
        results = dynamodb.execute_statement(Statement=statement)

        for item in results["Items"]:
            yield item

        while "NextToken" in results:
            results = dynamodb.execute_statement(Statement=statement, NextToken=results["NextToken"])

            for item in results["Items"]:
                yield item

    @classmethod
    def _select_deleted_hashes(cls, incoming_hashes, current_hashes):
        deleted_hashes = current_hashes[~current_hashes.pk.isin(incoming_hashes.pk)].reset_index(drop=True)

        LOGGER.debug('Deleted Data: %s', deleted_hashes)

        return deleted_hashes.to_dict(orient='records')

    def _delete_keywords_from_table(self, deleted_hashes, table, dynamodb):
        keyword_data = []

        for item in deleted_hashes:
            results = self._paginate(dynamodb,
                                     f"SELECT * FROM \"CPT-API-snomed-sbx\" WHERE pk='{item['pk']}' and begins_with(\"sk\", 'KEYWORD:')")
            keyword_data.extend(list(results))

        self._delete_from_table([dict(pk=item['pk']['S'], sk=item['sk']['S']) for item in keyword_data], table)

    def _delete_cpt_mappings_from_table(self, deleted_hashes, table):
        deleted_mappings = []
        for item in deleted_hashes:
            deleted_mappings.append({
                'pk': item['pk'].rsplit(':', 2)[0],
                'sk': item['pk'].split(':', 2)[2]
            })

        self._delete_from_table(deleted_mappings, table)

    def _delete_hashes_from_table(self, deleted_hashes, table):
        self._delete_from_table(deleted_hashes, table)

    @classmethod
    def _select_new_hashes(cls, incoming_hashes, current_hashes):
        new_or_updated_hashes = incoming_hashes[~incoming_hashes.sk.isin(current_hashes.sk)].reset_index(drop=True)

        new_hashes = new_or_updated_hashes[~new_or_updated_hashes.pk.isin(current_hashes.pk)].reset_index(drop=True)

        LOGGER.debug('Added Data: %s', new_hashes)

        return new_hashes.to_dict(orient='records')

    def _add_keywords_to_table(self, new_data, table, incoming_data):
        keywords = []
        for item in new_data:
            for data in incoming_data:
                if item["pk"] == data['pk']:
                    keywords.append([data])

        self._add_to_table(keywords, table)

    def _add_cpt_mappings_to_table(self, new_data, table, incoming_data):
        mappings = []

        for item in new_data:
            for data in incoming_data:
                if data['pk'] == item['pk'].rsplit(':', 2)[0] and data['sk'] == item['pk'].split(':', 2)[2]:
                    mappings.append(data)

        self._add_to_table(mappings, table)

    def _add_hashes_to_table(self, new_data, table):
        self._add_to_table(new_data, table)

    @classmethod
    def _select_updated_hashes(cls, incoming_hashes, current_hashes):
        new_or_updated_hashes = incoming_hashes[~incoming_hashes.sk.isin(current_hashes.sk)]

        updated_hashes = new_or_updated_hashes[new_or_updated_hashes.pk.isin(current_hashes.pk)]

        LOGGER.debug('Updated Data: %s', updated_hashes)

        return updated_hashes.to_dict(orient='records')

    @classmethod
    def _get_updated_old_hashes(cls, updated_hashes, current_hashes):
        old_hashes = []

        for updated_hash in updated_hashes:
            for current_hash in current_hashes:
                if current_hash['pk'] == updated_hash['pk']:
                    old_hashes.append(current_hash)

        return old_hashes

    def _get_old_keywords(self, updated_hashes, dynamodb):
        updated_old_keywords = []

        for item in updated_hashes:
            results = self._paginate(dynamodb, f"SELECT * FROM \"CPT-API-snomed-sbx\" WHERE pk='{item['pk']}' "
                                               f"and begins_with(\"sk\", 'KEYWORD:')")
            updated_old_keywords.extend(list(results))

        return updated_old_keywords

    @classmethod
    def _get_updated_keywords(cls, updated_hashes, incoming_data):
        incoming_keywords = []

        for hash_item in updated_hashes:
            for data in incoming_data:
                if hash_item['pk'] == data['pk']:
                    incoming_keywords.append(data)

        return incoming_keywords

    def _update_cpt_mappings_in_table(self, updated_hashes, table, incoming_data):
        for item in updated_hashes:
            for data in incoming_data:
                self._update_in_table(data, item, table)

    @classmethod
    def _delete_from_table(cls, data, table):
        with table.batch_writer() as batch:
            for item in data:
                batch.delete_item(Key={
                    'pk': item['pk'],
                    'sk': item['sk']
                })
                LOGGER.debug('Deleted Item: %s', item['pk'])

    @classmethod
    def _add_to_table(cls, data, table):
        with table.batch_writer() as batch:
            for item in data:
                batch.put_item(Item=item)
                LOGGER.debug('Added Item: %s', item['pk'])

    def _replace_in_table(self, old_data, new_data, table):
        self._delete_from_table(old_data, table)
        self._add_to_table(new_data, table)

    @classmethod
    def _update_in_table(cls, data, item, table):
        if data["pk"] == item['pk'].rsplit(':', 2)[0] and data['sk'] == item['pk'].split(':', 2)[2]:
            table.update_item(
                Key={
                    'pk': data['pk'],
                    'sk': data['sk']
                },
                UpdateExpression='SET snomed_descriptor=:s, map_category=:m, cpt_descriptor=:c',
                ExpressionAttributeValues={
                    ':s': data['snomed_descriptor'],
                    ':m': data['map_category'],
                    ':c': data['cpt_descriptor']
                }
            )
            LOGGER.debug('Updated Mapping: %s', data['pk'])
