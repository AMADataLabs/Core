""" Transformer base class and NO-OP implementation. """
from   abc import ABC, abstractmethod

import tempfile

import logging
import pandas

import dask.dataframe

from   datalabs.etl.task import ETLComponentTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class TransformerTask(ETLComponentTask, ABC):
    def run(self):
        self._data = self._transform()

    @abstractmethod
    def _transform(self) -> 'Transformed Data':
        pass


class PassThroughTransformerTask(TransformerTask):
    def _transform(self):
        log_data = self._parameters.get('LOG_DATA')
        if log_data and log_data.upper() == 'TRUE':
            LOGGER.info('Passed-through Data: %s', self._parameters['data'])
        return self._parameters['data']


class ScalableTransformerMixin():
    @classmethod
    def _csv_to_dataframe(cls, path, on_disk: bool, **kwargs):
        if on_disk is True:
            data = dask.dataframe.read_csv(path, dtype=str, **kwargs)
        else:
            data = pandas.read_csv(path, dtype=str, **kwargs)

        return data

    @classmethod
    def _dataframe_to_csv(cls, data, on_disk: bool, **kwargs):
        if on_disk is True:
            path = tempfile.NamedTemporaryFile(delete=False).name
            data = data.to_csv(path, single_file=True, index=False, **kwargs)[0]
        else:
            data = data.to_csv(data, index=False)

        return data
