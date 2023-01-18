''' MySQL ORM loader provider '''
import csv
import hashlib
import logging
import re

import pandas

import datalabs.etl.orm.provider.base

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class ORMLoaderProvider(datalabs.etl.orm.provider.base.ORMLoaderProvider):
    def get_primary_key(self, database, schema, table):
        query = None

        if schema:
            table = f'{schema}.{table}'

        query = f"SHOW KEYS FROM {table} WHERE Key_name = 'PRIMARY'"

        primary_key_table = database.read(query)

        return primary_key_table["Column_name"][0]

    def get_database_columns(self, database, schema, table):
        schema_clause = ""

        if schema:
            schema_clause = f"table_schema = '{schema}' AND "

        query = "SELECT * FROM information_schema.columns " \
                f"WHERE {schema_clause}table_name = '{table}';"
        column_data = database.read(query)

        columns = column_data["COLUMN_NAME"].to_list()
        LOGGER.debug('Columns in table %s.%s: %s', schema, table, columns)

        return columns

    # pylint: disable=too-many-arguments
    def get_current_row_hashes(self, database, schema, table, primary_key, columns):
        get_current_hash = None

        if schema:
            table = f'{schema}.{table}'

        get_current_hash = f"""
            SELECT {primary_key}, MD5(CAST(CONCAT({','.join(columns)}) AS CHAR CHARACTER SET utf8)) as md5
            FROM {table}
        """

        current_hashes = database.read(get_current_hash).astype(str)
        LOGGER.debug('Current Row Hashes: %s', current_hashes)

        return current_hashes

    @classmethod
    def generate_row_hashes(cls, data, primary_key, columns):
        csv_data = data[columns].to_csv(header=None, index=False, quoting=csv.QUOTE_NONE, escapechar='$')
        row_strings = re.sub(r'([^$]),', r'\1', csv_data).strip('\n').replace('$,', ',')
        incoming_hashes = pandas.DataFrame(columns=[primary_key, 'md5'])

        if row_strings:
            hashes = [hashlib.md5(row_string.encode('utf-8')).hexdigest() for row_string in row_strings.split('\n')]
            primary_keys = data[primary_key].tolist()

            incoming_hashes = pandas.DataFrame({primary_key: primary_keys, 'md5': hashes})

        LOGGER.debug('Incoming Row Hashes: %s', incoming_hashes)

        return incoming_hashes
