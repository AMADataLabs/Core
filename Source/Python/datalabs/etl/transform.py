""" Transformer base class and NO-OP implementation. """
from   abc import ABC, abstractmethod
from   io import BytesIO

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
            csv = data.to_csv(path, single_file=True, index=False, **kwargs)[0].encode()
        else:
            csv = data.to_csv(index=False).encode()

        return csv
