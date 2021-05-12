""" Classes for loading AIMS data for POLO analysis """
from   enum import Enum
import gc
import logging
import re
import sys

import pandas

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class DataFileFormat(Enum):
    CSV = 'csv'
    FEATHER = 'feather'


class EntityTableCleaner():
    TIMESTAMP_REGEX = re.compile('(?P<date>[0-9]{4}/[0-9]{2}/[0-9]{2}):(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})')

    # pylint: disable=too-many-arguments
    def __init__(
            self, input_path: str, output_path: str,
            row_filters: dict = None, column_filters: dict = None, types: dict = None, defaults: dict = None,
            datestamp_columns: list = None
    ):
        self._input_path = input_path
        self._output_path = output_path
        self._row_filters = row_filters or {}
        self._column_filters = column_filters or {}
        self._types = types or {}
        self._defaults = defaults or {}
        self._datestamp_columns = datestamp_columns or {}

    def clean(self):
        gc.collect()

        table_chunks = self._read_table_from_file(self._input_path)
        LOGGER.debug('Table chunk iterator: %s', table_chunks)

        LOGGER.info('Cleaning data')
        clean_table = self._clean_chunked_table(table_chunks)

        self._write_table_to_file(clean_table, self._output_path)

        del table_chunks
        gc.collect()

    @classmethod
    def _read_table_from_file(cls, filename):
        extension = filename.rsplit('.')[-1]
        LOGGER.debug('File extension: %s', extension)
        table_chunks = None

        if extension == DataFileFormat.CSV.value:
            LOGGER.info('Reading CSV file %s', filename)
            table_chunks = cls._read_csv_file_in_chunks(filename)
        elif extension == DataFileFormat.FEATHER.value:
            LOGGER.info('Reading Feather file %s', filename)
            table_chunks = cls._read_feather_file_in_chunks(filename)
        else:
            raise ValueError(f"Unsupported input data file extension '{extension}'")

        return table_chunks

    def _clean_chunked_table(self, table_chunks) -> pandas.DataFrame:
        cleaned_table_chunks = []

        for chunk in table_chunks:
            cleaned_chunk = self._clean_table(chunk)
            sys.stdout.write('.')
            sys.stdout.flush()
            LOGGER.debug('Cleaned chunk: %s', cleaned_chunk)

            cleaned_table_chunks.append(cleaned_chunk)
        sys.stdout.write('\n')
        sys.stdout.flush()

        cleaned_table = pandas.concat(cleaned_table_chunks)
        cleaned_table.reset_index(inplace=True)
        LOGGER.debug('Cleaned table: %s', cleaned_table)

        return cleaned_table

    @classmethod
    def _write_table_to_file(cls, table, filename):
        extension = filename.rsplit('.')[-1]

        if extension == DataFileFormat.CSV.value:
            LOGGER.info('Writing CSV file %s', filename)
            table.to_csv(filename)
        elif extension == DataFileFormat.FEATHER.value:
            LOGGER.info('Writing Feather file %s', filename)
            table.to_feather(filename)
        else:
            raise ValueError(f"Unsupported input data file extension '{extension}'")

    @classmethod
    def _read_csv_file_in_chunks(cls, filename, chunksize=100000):
        return pandas.read_csv(filename, dtype=str, na_values=['', '(null)'], chunksize=chunksize)

    @classmethod
    def _read_feather_file_in_chunks(cls, filename):
        yield pandas.read_feather(filename)

    def _clean_table(self, table: pandas.DataFrame) -> pandas.DataFrame:
        table = self._filter_table(table)
        LOGGER.debug('Filtered Table: %s', table)

        if not table.empty:
            LOGGER.debug('Table before cleaning: %s', table)
            table = self._clean_values(table)
            LOGGER.debug('Table after cleaning: %s', table)

        table = self._refactor_columns(table)

        return table

    def _filter_table(self, table):
        table = self._filter_rows(table, self._row_filters)

        table = self._filter_columns(table, self._column_filters)

        return table

    def _clean_values(self, table):
        LOGGER.debug('Table before datestamp standardization: %s', table)
        table = self._standardize_datestamps(table, self._datestamp_columns)
        LOGGER.debug('Table after datestamp standardization: %s', table)

        table = self._strip_values(table)

        table = self._insert_defaults(table, self._defaults)

        table = self._datestamp_to_datetime(table, self._datestamp_columns)

        return table

    def _refactor_columns(self, table):
        table = self._set_column_types(table, self._types)

        table = self._rename_columns(table, self._column_filters)

        return table

    @classmethod
    def _filter_rows(cls, table: pandas.DataFrame, filters: dict) -> pandas.DataFrame:
        for name, value in filters.items():
            table = table[table[name] == value]

        return table

    @classmethod
    def _filter_columns(cls, table: pandas.DataFrame, filters: dict) -> pandas.DataFrame:
        column_names = filters.keys()
        if column_names:
            table = table[column_names]

        return table

    @classmethod
    def _standardize_datestamps(cls, table, column_names):
        for column_name in column_names:
            table[column_name] = cls._standardize_datestamps_in_column(table[column_name])

        LOGGER.debug('Table: %s', table[column_names])

        return table

    @classmethod
    def _strip_values(cls, table):
        for column_name in table.columns.values:
            column = table[column_name]

            try:
                # column[~column.isna()] = column[~column.isna()].apply(str.strip)
                table.loc[~column.isna(), column_name] = column[~column.isna()].apply(str.strip)
            except TypeError:
                LOGGER.warning("Non-string type '%s' for column '%s'", table[column_name].dtype, column_name)
            except Exception as exception:
                LOGGER.debug('Bad column %s:\n%s', column_name, column[~column.isna()])
                raise exception

        return table

    @classmethod
    def _insert_defaults(cls, table, defaults):
        for column_name, default_value in defaults.items():
            table[column_name].fillna(default_value, inplace=True)

        return table

    @classmethod
    def _datestamp_to_datetime(cls, table, columns):
        for column in columns:
            table[column] = pandas.to_datetime(table[column], errors='coerce')

        return table

    @classmethod
    def _set_column_types(cls, table: pandas.DataFrame, types: dict) -> pandas.DataFrame:
        for column_name, type_name in types.items():
            table[column_name] = table[column_name].astype(type_name)

        return table

    @classmethod
    def _rename_columns(cls, table: pandas.DataFrame, filters: dict) -> pandas.DataFrame:
        table.rename(columns=filters, inplace=True)

        return table

    @classmethod
    def _standardize_datestamps_in_column(cls, column):
        string_values = column[~column.isna()]

        string_values = string_values.str.replace('[', '')
        string_values = string_values.str.replace(']', '')
        string_values = string_values.apply(cls._make_parsable_timestamp)

        column[~column.isna()] = string_values
        LOGGER.debug('Column: %s', column)

        return column

    @classmethod
    def _make_parsable_timestamp(cls, timestamp):
        match = cls.TIMESTAMP_REGEX.match(timestamp)
        parsable_timestamp = timestamp

        if match:
            parsable_timestamp = '{} {}'.format(match.group('date'), match.group('time'))

        return parsable_timestamp
