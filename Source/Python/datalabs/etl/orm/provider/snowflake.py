''' Snowflake ORM loader provider '''
import csv
import hashlib
import re

import pandas

import datalabs.etl.orm.provider.base


class ORMLoaderProvider(datalabs.etl.orm.provider.base.ORMLoaderProvider):
    def get_primary_key(self, database, schema, table):
        query = None

        if schema:
            table = f'{schema}.{table}'

        query = f"SHOW PRIMARY KEYS IN {table}"

        primary_key_table = database.read(query)

        return primary_key_table["column_name"][0].lower()

    def get_database_columns(self, database, schema, table):
        query = None

        if schema:
            table_name = f'{table}'

        query = f"SHOW COLUMNS IN TABLE {table_name};"

        column_data = database.read(query)

        columns = column_data["column_name"].str.lower().to_list()

        return columns

    # pylint: disable=too-many-arguments
    def get_current_row_hashes(self, database, schema, table, primary_key, columns):
        get_current_hash = None

        if schema:
            table = f'{schema}.{table}'

        get_current_hash = f"""
            SELECT {primary_key},
            MD5(CAST(COALESCE(CONCAT({','.join(columns)}), '') AS VARCHAR)) as md5
            FROM {table}
        """

        current_hashes = database.read(get_current_hash).astype(str)

        return current_hashes


    @classmethod
    def generate_row_hashes(cls, data, primary_key, columns):
        csv_data = data[columns].to_csv(header=None, index=False, quoting=csv.QUOTE_NONE, escapechar='$')
        row_strings = re.sub(r'([^$]),', r'\1', csv_data).strip('\n').replace('$,', ',').split('\n')

        hashes = [hashlib.md5(row_string.encode('utf-8')).hexdigest() for row_string in row_strings]
        primary_keys = data[primary_key].tolist()

        incoming_hashes = pandas.DataFrame({primary_key: primary_keys, 'md5': hashes})

        return incoming_hashes
