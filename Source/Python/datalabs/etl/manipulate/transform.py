""" DataFrame manipulation transformers. """
from   dataclasses import dataclass
from   io import BytesIO
import logging

import numpy
import pandas

from   datalabs.etl.transform import TransformerTask
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class DataFrameTransformerMixin:
    @classmethod
    def _csv_to_dataframe(cls, data, **kwargs):
        return pandas.read_csv(BytesIO(data), dtype=str, **kwargs)

    @classmethod
    def _dataframe_to_csv(cls, data, **kwargs):
        return data.to_csv(index=False, **kwargs).encode()


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SplitTransformerParameters:
    count: str
    execution_time: str = None
    data: object = None


class SplitTransformerTask(DataFrameTransformerMixin, TransformerTask):
    PARAMETER_CLASS = SplitTransformerParameters

    def _transform(self):
        count = int(self._parameters.count)
        datasets = [self._csv_to_dataframe(data) for data in self._parameters.data]
        split_datasets = []

        for dataset in datasets:
            split_datasets += numpy.array_split(dataset, count)

        return [self._dataframe_to_csv(dataset) for dataset in split_datasets]


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ConcatenateTransformerParameters:
    execution_time: str = None
    data: object = None


class ConcatenateTransformerTask(DataFrameTransformerMixin, TransformerTask):
    PARAMETER_CLASS = ConcatenateTransformerParameters

    def _transform(self):
        parts = [self._csv_to_dataframe(data) for data in self._parameters.data]

        data = pandas.concat(parts, ignore_index=True)

        return [self._dataframe_to_csv(data)]
