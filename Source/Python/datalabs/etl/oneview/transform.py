""" OneView Transformer"""
from   abc import ABC, abstractmethod

import csv
import logging
from   io import BytesIO
import tempfile

import pandas

import datalabs.etl.transform as etl
import datalabs.feature as feature

if feature.enabled("PROFILE"):
    from guppy import hpy

if feature.enabled("DASK"):
    import dask.dataframe


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ScalableTransformerMixin():
    @classmethod
    def _csv_to_dataframe(cls, data, on_disk: bool, **kwargs):
        if on_disk:
            dataframe = dask.dataframe.read_csv(data.decode(), dtype=str, **kwargs)
        else:
            dataframe = pandas.read_csv(BytesIO(data), dtype=str, **kwargs)

        return dataframe

    @classmethod
    def _dataframe_to_csv(cls, data, on_disk: bool, **kwargs):
        if on_disk:
            path = tempfile.NamedTemporaryFile(delete=False).name
            csv_data = data.to_csv(path, single_file=True, index=False, **kwargs)[0].encode()
        else:
            csv_data = data.to_csv(index=False).encode()

        return csv_data


class TransformerTask(ScalableTransformerMixin, etl.TransformerTask, ABC):
    def _transform(self):
        LOGGER.debug(self._parameters['data'])
        on_disk = bool(self._parameters.get("on_disk") and self._parameters["on_disk"].upper() == 'TRUE')

        if feature.enabled("PROFILE"):
            LOGGER.info('Pre csv to dataframes memory (%s)', hpy().heap())

        table_data = [self._csv_to_dataframe(data, on_disk) for data in self._parameters['data']]

        if feature.enabled("PROFILE"):
            LOGGER.info('Post csv to dataframes memory (%s)', hpy().heap())

        preprocessed_data = self._preprocess_data(table_data)

        if feature.enabled("PROFILE"):
            LOGGER.info('Post processed dataframes memory (%s)', hpy().heap())

        selected_data = self._select_columns(preprocessed_data)
        renamed_data = self._rename_columns(selected_data)

        postprocessed_data = self._postprocess_data(renamed_data)

        return [self._dataframe_to_csv(data, on_disk, quoting=csv.QUOTE_NONNUMERIC) for data in postprocessed_data]

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
