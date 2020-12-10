""" Oneview Transformer"""
from   abc import ABC, abstractmethod
import csv
import logging

import datalabs.etl.transform as etl

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class TransformerTask(etl.TransformerTask, ABC):
    def _transform(self):
        LOGGER.info(self._parameters.data)
        selected_data = self._select_columns(self._parameters.data)
        renamed_data = self._rename_columns(selected_data)

        return [self._dataframe_to_csv(data) for data in renamed_data]

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
    def _dataframe_to_csv(cls, data):
        return data.to_csv(index=False, quoting=csv.QUOTE_NONNUMERIC)
