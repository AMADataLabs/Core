""" Transformer base class and NO-OP implementation. """
import dask.dataframe

from abc import ABC, abstractmethod

from datalabs.etl.task import ETLComponentTask


class TransformerTask(ETLComponentTask, ABC):
    def run(self):
        self._data = self._transform()

    @abstractmethod
    def _transform(self) -> 'Transformed Data':
        pass


class PassThroughTransformerTask(TransformerTask):
    def _transform(self):
        return self._parameters['data']


class ScalableTransformerMixin(TransformerTask, ABC):
    def _csv_to_dataframe(self, path: str, **kwargs) -> dask.dataframe:
        return dask.dataframe.read_csv(path, **kwargs)

    def _dataframe_to_csv(self, data: dask.dataframe.DataFrame, **kwargs):
        path = 'data.csv'
        return data.to_csv(path, dtype=str, **kwargs)
