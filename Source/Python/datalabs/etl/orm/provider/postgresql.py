''' PostgreSQL ORM loader provider '''
import csv
import hashlib
import logging
import re

import numpy as np
import pandas
from psycopg2.extensions import register_adapter, AsIs

import datalabs.etl.orm.provider.base

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

def adapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)

register_adapter(np.int64, adapt_numpy_int64)


class ORMLoaderProvider(datalabs.etl.orm.provider.base.ORMLoaderProvider):
    def get_primary_key(self, database, schema, table):
        query = None

        if schema:
            table = f'{schema}.{table}'

        query = "SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type "\
                "FROM pg_index i JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) " \
                f"WHERE  i.indrelid = '{table}'::regclass AND i.indisprimary"

        primary_key_table = database.read(query)

        return primary_key_table["attname"][0]

    def get_database_columns(self, database, schema, table):
        schema_clause = ""

        if schema:
            schema_clause = f"table_schema = '{schema}' AND "

        query = "SELECT * FROM information_schema.columns " \
                f"WHERE {schema_clause}table_name = '{table}';"
        column_data = database.read(query)

        columns = column_data["column_name"].to_list()
        LOGGER.debug('Columns in table %s.%s: %s', schema, table, columns)

        return columns

    # pylint: disable=too-many-arguments
    def get_current_row_hashes(self, database, schema, table, primary_key, columns):
        columns = [self._quote_keyword(column) for column in columns]

        if schema:
            table = f'{schema}.{table}'

        get_current_hash = f"SELECT {primary_key}, md5(({','.join(columns)})::TEXT) as md5 FROM {table}"

        current_hashes = database.read(get_current_hash).astype(str)
        LOGGER.debug('Current Row Hashes: %s', current_hashes)

        return current_hashes

    @classmethod
    def generate_row_hashes(cls, data, primary_key, columns):
        csv_data = data[columns].to_csv(header=None, index=False, quoting=csv.QUOTE_ALL).strip('\n').split('\n')
        row_strings = ["(" + cls._standardize_row_text(i) + ")" for i in csv_data]

        hashes = [hashlib.md5(row_string.encode('utf-8')).hexdigest() for row_string in row_strings]
        primary_keys = data[primary_key].tolist()

        incoming_hashes = pandas.DataFrame({primary_key: primary_keys, 'md5': hashes})
        LOGGER.debug('Incoming Row Hashes: %s', incoming_hashes)

        return incoming_hashes

    @classmethod
    def _quote_keyword(cls, column):
        quoted_column = column

        if column in ['group', 'primary']:
            quoted_column = f'"{column}"'

        return quoted_column

    @classmethod
    def _standardize_row_text(cls, csv_string):
        # split at only unquoted commas
        columns = [term for term in re.split(r'("[^"]*,[^"]*"|[^,]*)', csv_string) if (term and term != ',')]

        simplified_boolean_columns = [cls._replace_boolean(column) for column in columns]

        return ','.join(cls._unquote_term(column) for column in simplified_boolean_columns)

    @classmethod
    def _replace_boolean(cls, quoted_column):
        column = quoted_column

        if quoted_column == '"True"':
            column = '"t"'
        elif quoted_column == '"False"':
            column = '"f"'

        return column

    @classmethod
    def _unquote_term(cls, csv_column):
        quoted_csv_column = csv_column
        match = re.match(r'".*[, ].*"', csv_column)  # match quoted strings with spaces or commas

        if match is None:
            quoted_csv_column = f'{csv_column[1:-1]}'

        return quoted_csv_column
