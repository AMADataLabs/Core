#!/usr/bin/env python

from   abc import ABC, abstractmethod
from   collections import namedtuple
from   datetime import datetime
from   enum import Enum
import gc
import logging
import os
import re

import pandas

import settings

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class DataFileFormat(Enum):
    CSV = 'csv'
    Feather = 'feather'


class EntityTableCleaner():
    def __init__(
        self, input_path: str, output_path: str,
        row_filters: dict=None, column_filters: dict=None, types: dict=None
    ):
        self._input_path = input_path
        self._output_path = output_path
        self._row_filters = row_filters or {}
        self._column_filters = column_filters or {}
        self._types = types or {}

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
        LOGGER.debug(f'File extension: {extension}')
        table_chunks = None

        if extension == DataFileFormat.CSV.value:
            LOGGER.info('Reading CSV file %s', filename)
            table_chunks = cls._read_csv_file_in_chunks(filename)
        elif extension == DataFileFormat.Feather.value:
            LOGGER.info('Reading Feather file %s', filename)
            table_chunks = cls._read_feather_file_in_chunks(filename)
        else:
            raise ValueError(f"Unsupported input data file extension '{extension}'")

        return table_chunks

    def _clean_chunked_table(self, table_chunks) -> pandas.DataFrame:
        cleaned_table_chunks = []

        for chunk in table_chunks:
            cleaned_chunk = self._clean_table(chunk)
            LOGGER.debug('Cleaned chunk: %s', cleaned_chunk)

            cleaned_table_chunks.append(cleaned_chunk)

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
        elif extension == DataFileFormat.Feather.value:
            LOGGER.info('Writing Feather file %s', filename)
            table.to_feather(filename)
        else:
            raise ValueError(f"Unsupported input data file extension '{extension}'")

    @classmethod
    def _read_csv_file_in_chunks(cls, filename):
        return pandas.read_csv(filename, dtype=str, na_values=['', '(null)'], chunksize=10000)

    @classmethod
    def _read_feather_file_in_chunks(cls, filename):
        yield pandas.read_feather(filename)

    def _clean_table(self, table: pandas.DataFrame) -> pandas.DataFrame:
        table = self._filter_table(table)

        if not table.empty:
            table = self._clean_values(table)

        table = self._refactor_columns(table)

        return table

    def _filter_table(self, table):
        table = self._filter_rows(table, self._row_filters)

        table = self._filter_columns(table, self._column_filters)

        return table

    def _clean_values(self, table):
        table = self._strip_values(table)

        return table

    def _refactor_columns(self, table):
        table = self._set_column_types(table, self._types)

        table = self._rename_columns(table, self._column_filters)

        return table

    @classmethod
    def _filter_rows(cls, table: pandas.DataFrame, filters: dict) -> pandas.DataFrame:
        for name,value in filters.items():
            table = table[table[name] == value]

        return table

    @classmethod
    def _filter_columns(cls, table: pandas.DataFrame, filters: dict) -> pandas.DataFrame:
        column_names = filters.keys()
        if column_names:
            table = table[column_names]

        return table

    @classmethod
    def _strip_values(cls, table):
        for col in table.columns.values:
            try:
                table[col] = table[col].apply(str.strip)
            except Exception as e:
                LOGGER.warn('Bad column %s:\n%s', col, table[table[col].isna()][col])
                # raise e

        return table

    @classmethod
    def _set_column_types(cls, table: pandas.DataFrame, types: dict) -> pandas.DataFrame:
        return table

    @classmethod
    def _rename_columns(cls, table: pandas.DataFrame, filters: dict) -> pandas.DataFrame:
        table.rename(columns=filters, inplace=True)

        return table


class EntityCommCleaner(EntityTableCleaner):
    TIMESTAMP_REGEX = re.compile('(?P<date>[0-9]{4}/[0-9]{2}/[0-9]{2}):(?P<time>[0-9]{2}:[0-9]{2}:[0-9]{2})')

    def __init__(
        self, input_path: str, output_path: str,
        row_filters: dict=None, column_filters: dict=None, types: dict=None, datestamp_columns: list=None
    ):
        super().__init__(
            input_path, output_path,
            row_filters=row_filters, column_filters=column_filters, types=types
        )

        self._datestamp_columns = datestamp_columns

    def _clean_values(self, table):
        table = self._standardize_datestamps(table, self._datestamp_columns)
        table = self._strip_values(table)
        table = self._datestamp_to_datetime(table, self._datestamp_columns)

        return table

    @classmethod
    def _set_column_types(cls, table: pandas.DataFrame, types: dict) -> pandas.DataFrame:
        for column_name,type_name in types.items():
            table[column_name] = table['entity_id'].astype(type_name)
            table[column_name] = table['comm_id'].astype(type_name)

        return table

    @classmethod
    def _standardize_datestamps(cls, table, columns):
        for column in columns:
            table[column].fillna(datetime.now().strftime('%Y/%m/%d'), inplace=True)
            table[column] = table[column].str.replace('[', '')
            table[column] = table[column].str.replace(']', '')
            table[column] = table[column].apply(cls._make_parsable_timestamp)
            LOGGER.debug('Column: %s', table[column])

        return table

    @classmethod
    def _datestamp_to_datetime(cls, table, columns):
        for column in columns:
            table[column] = pandas.to_datetime(table[column])

        return table

    @classmethod
    def _make_parsable_timestamp(cls, timestamp):
        match = cls.TIMESTAMP_REGEX.match(timestamp)
        parsable_timestamp = timestamp

        if match:
            parsable_timestamp = '{} {}'.format(match.group('date'), match.group('time'))

        return parsable_timestamp


class EntityCommAtCleaner(EntityCommCleaner):
    def __init__(self, input_path, output_path):
        column_names = 'entity_id', 'comm_type', 'begin_dt', 'comm_id', 'end_dt', 'src_cat_code'
        column_filters = {name:'ent_comm_'+name for name in column_names}

        super().__init__(
            input_path,
            output_path,
            row_filters={'comm_cat': 'A '},
            column_filters=column_filters,
            types={'entity_id': 'uint32'},
            datestamp_columns=['begin_dt', 'end_dt']
        )


class EntityCommUsgCleaner(EntityCommCleaner):
    def __init__(self, input_path, output_path):
        column_names = ['entity_id', 'comm_type', 'comm_usage', 'usg_begin_dt', 'comm_id', 'comm_type',
                        'end_dt', 'src_cat_code']
        column_filters = {name:'usg_'+name for name in column_names}

        super().__init__(
            input_path,
            output_path,
            row_filters={'comm_cat': 'A '},
            column_filters=column_filters,
            types={'entity_id': 'uint32'},
            datestamp_columns=['usg_begin_dt', 'end_dt']
        )


class PostAddrAtCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        column_names = ['comm_id', 'addr_line2', 'addr_line1', 'addr_line0', 'city_cd',
                        'state_cd', 'zip', 'plus4']
        column_filters = {name:'post_'+name for name in column_names}

        super().__init__(
            input_path,
            output_path,
            column_filters=column_filters,
            types={'comm_id': 'uint32'}
        )

    @classmethod
    def _set_column_types(cls, table: pandas.DataFrame, types: dict) -> pandas.DataFrame:
        for column_name,type_name in types.items():
            table[column_name] = table['comm_id'].astype(type_name)

        return table


class LicenseLtCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        super().__init__(
            input_path,
            output_path,
            types={'entity_id': 'uint32'}
        )

    def _clean_values(self, table):
        table = self._strip_values(table)
        table = self._insert_default_comm_id(table)

        return table

    @classmethod
    def _set_column_types(cls, table: pandas.DataFrame, types: dict) -> pandas.DataFrame:
        for column_name,type_name in types.items():
            table[column_name] = table['entity_id'].astype(type_name)
            table[column_name] = table['comm_id'].astype(type_name)

        return table

    @classmethod
    def _insert_default_comm_id(cls, table):
        table['comm_id'].fillna('0', inplace=True)

        return table


class EntityKeyEtCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        super().__init__(
            input_path,
            output_path,
            types={'entity_id': 'uint32'}
        )

    @classmethod
    def _set_column_types(cls, table: pandas.DataFrame, types: dict) -> pandas.DataFrame:
        for column_name,type_name in types.items():
            table[column_name] = table['entity_id'].astype(type_name)

        return table
