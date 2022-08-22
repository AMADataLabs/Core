""" OneView Transformer"""
from   abc import ABC, abstractmethod

import csv
import logging

from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
import datalabs.etl.transform as etl
from   datalabs import feature

if feature.enabled("PROFILE"):
    from guppy import hpy


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class TransformerTask(CSVReaderMixin, CSVWriterMixin, etl.TransformerTask, ABC):
    def _transform(self):
        LOGGER.debug(self._parameters['data'])

        if feature.enabled("PROFILE"):
            LOGGER.info('Pre csv to dataframes memory (%s)', hpy().heap())

        table_data = [self._csv_to_dataframe(data) for data in self._parameters['data']]

        if feature.enabled("PROFILE"):
            LOGGER.info('Post csv to dataframes memory (%s)', hpy().heap())

        preprocessed_data = self._preprocess_data(table_data)

        if feature.enabled("PROFILE"):
            LOGGER.info('Post processed dataframes memory (%s)', hpy().heap())

        selected_data = self._select_columns(preprocessed_data)
        renamed_data = self._rename_columns(selected_data)

        postprocessed_data = self._postprocess_data(renamed_data)

        return [self._dataframe_to_csv(data, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]

    @classmethod
    def _preprocess_data(cls, data):
        return data

    def _select_columns(self, dataset):
        names = [list(column_map.keys()) for column_map in self._get_columns()]
        LOGGER.info(names)
        return [data[name] for name, data in zip(names, dataset)]

    def _rename_columns(self, dataset):
        column_maps = self._get_columns()

        return [data.rename(columns=column_map) for data, column_map in zip(dataset, column_maps)]

    @abstractmethod
    def _get_columns(self):
        return []

    @classmethod
    def _postprocess_data(cls, data):
        return data
