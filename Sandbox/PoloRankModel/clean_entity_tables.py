#!/usr/bin/env python

from   abc import ABC, abstractmethod
from   collections import namedtuple
import gc
import logging
import os

import pandas as pd

import settings


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class EntityTableCleaner():
    def __init__(self, input_path, output_path):
        self._input_path = input_path
        self._output_path = output_path

    def clean(self):
        gc.collect()

        LOGGER.info('Reading CSV file %s', self._input_path)
        table = pd.read_csv(self._input_path, dtype=str)

        LOGGER.info('Cleaning data')
        clean_table = self._clean_table(table)

        LOGGER.info('Writing Feather file %s', self._output_path)
        clean_table.to_feather(self._output_path)

        del table
        gc.collect()

    def _clean_table(self, table: pd.DataFrame) -> pd.DataFrame:
        table = self._trim_table(table)

        table = self._strip_table(table)

        return table

    @classmethod
    def _trim_table(cls, table: pd.DataFrame) -> pd.DataFrame:
        return table

    @classmethod
    def _strip_table(cls, table: pd.DataFrame) -> pd.DataFrame:
        return table


class EntityTableTrimmerMixin():
    @classmethod
    def _trim_table(cls, table):
        table['comm_cat'] = table['comm_cat'].apply(str.strip)
        table = table[table['comm_cat']=='A']

        return table

class EntityTableStripperMixin():
    @classmethod
    def _strip_table(cls, table):
        for col in table.columns.values:
            table[col] = table[col].apply(str.strip)

        return table


class EntityCommAtCleaner(EntityTableCleaner, EntityTableTrimmerMixin, EntityTableStripperMixin):
    pass


class EntityCommUsgCleaner(EntityTableCleaner, EntityTableTrimmerMixin, EntityTableStripperMixin):
    pass


class PostAddrAtCleaner(EntityTableCleaner, EntityTableStripperMixin):
    pass


class LicenseLtCleaner(EntityTableCleaner, EntityTableStripperMixin):
    pass


class EntityKeyEtCleaner(EntityTableCleaner, EntityTableStripperMixin):
    pass


Parameters = namedtuple('Parameters', 'input output cleaner')


def main():
    parameter_set = [
        Parameters(input='ENTITY_COMM_AT_FILE_RAW', output='ENTITY_COMM_AT_FILE', cleaner=EntityCommAtCleaner),
        Parameters(input='ENTITY_COMM_USG_FILE_RAW', output='ENTITY_COMM_USG_FILE', cleaner=EntityCommUsgCleaner),
        Parameters(input='POST_ADDR_AT_FILE_RAW', output='POST_ADDR_AT_FILE', cleaner=PostAddrAtCleaner),
        Parameters(input='LICENSE_LT_FILE_RAW', output='LICENSE_LT_FILE', cleaner=LicenseLtCleaner),
        Parameters(input='ENTITY_KEY_ET_FILE_RAW', output='ENTITY_KEY_ET_FILE', cleaner=EntityKeyEtCleaner),
    ]

    for parameters in parameter_set:
        input_file = os.environ.get(parameters.input)
        output_file = os.environ.get(parameters.output)
        LOGGER.info('--------------------------------')
        parameters.cleaner(input_file, output_file).clean()


if __name__ == '__main__':
    main()

