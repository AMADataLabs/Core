#!/usr/bin/env python

from   abc import ABC, abstractmethod
from   collections import namedtuple
from   enum import Enum
import gc
import logging
import os

import pandas as pd

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

        table = self._read_table_from_file(self._input_path)

        LOGGER.info('Cleaning data')
        clean_table = self._clean_table(table)

        self._write_table_to_file(table, self._output_path)

        del table
        gc.collect()

    @classmethod
    def _read_table_from_file(cls, filename):
        extension = filename.rsplit('.')[-1]
        LOGGER.debug(f'File extension: {extension}')
        table = None

        if extension == DataFileFormat.CSV.value:
            LOGGER.info('Reading CSV file %s', filename)
            table = pd.read_csv(filename, dtype=str, na_values=['', '(null)'])
        elif extension == DataFileFormat.Feather.value:
            LOGGER.info('Reading Feather file %s', filename)
            table = pd.read_feather(filename)
        else:
            raise ValueError(f"Unsupported input data file extension '{extension}'")

        return table

    def _clean_table(self, table: pd.DataFrame) -> pd.DataFrame:
        table = self._filter_rows(table, self._row_filters)

        table = self._filter_columns(table, self._column_filters)

        table = self._strip_values(table)

        table = self._set_column_types(table, self._types)

        table = self.__rename_columns(table, self._column_filters)

        return table

    @classmethod
    def _write_table_to_file(cls, table, filename):
        extension = filename.rstrip('.')[-1]
        table = None

        if extension == DataFileFormat.CSV.value:
            LOGGER.info('Writing CSV file %s', filename)
            table.to_csv(filename)
        elif extension == DataFileFormat.Feather.value:
            LOGGER.info('Writing Feather file %s', filename)
            table.to_feather(filename)
        else:
            raise ValueError(f"Unsupported input data file extension '{extension}'")

    @classmethod
    def _filter_rows(cls, table: pd.DataFrame, filters: dict) -> pd.DataFrame:
        for name,value in filters:
            table = table[table[name] == value]

        return table

    @classmethod
    def _filter_columns(cls, table: pd.DataFrame, filters: dict) -> pd.DataFrame:
        table = table[filters.keys()]

        return table

    @classmethod
    def _strip_values(cls, table):
        for col in table.columns.values:
            table[col] = table[col].apply(str.strip)

        return table

    @classmethod
    def _set_column_types(cls, table: pd.DataFrame, types: dict) -> pd.DataFrame:
        for column_name,type_name in types:
            table[column_name] = table['entity_id'].astype(type_name)

        return table

    @classmethod
    def _rename_columns(cls, table: pd.DataFrame, filters: dict) -> pd.DataFrame:
        table.rename(columns=filters, inplace=True)

        return table


class EntityCommAtCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        column_names = 'entity_id', 'comm_type', 'begin_dt', 'comm_id', 'end_dt', 'src_cat_code'
        column_filters = {name:'ent_comm_'+name for name in column_names}

        super().__init__(
            input_path,
            output_path,
            row_filters={'comm_cat': 'A '},
            column_filters=column_filters,
            types={'entity_id': 'uint32'}
        )


class EntityCommUsgCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        column_names = ['entity_id', 'comm_type', 'comm_usage', 'usg_begin_dt', 'comm_id', 'comm_type',
                        'end_dt', 'src_cat_code']
        column_filters = {name:'usg_'+name for name in column_names}

        super().__init__(
            input_path,
            output_path,
            row_filters={'comm_cat': 'A '},
            column_filters=column_filters,
            types={'entity_id': 'uint32'}
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


class LicenseLtCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        super().__init__(
            input_path,
            output_path,
            types={'entity_id': 'uint32'}
        )


class EntityKeyEtCleaner(EntityTableCleaner):
    def __init__(self, input_path, output_path):
        super().__init__(
            input_path,
            output_path,
            types={'entity_id': 'uint32'}
        )

