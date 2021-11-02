""" DataFrame manipulation transformers. """
from   dataclasses import dataclass
from   io import BytesIO
import itertools
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
        return pandas.read_csv(BytesIO(data), dtype=object, **kwargs)

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


class ConcatenateTransformerTask(TransformerTask):
    PARAMETER_CLASS = ConcatenateTransformerParameters

    def _transform(self):
        line_sets = [data.strip().split(b'\n') for data in self._parameters.data]
        lines = list(itertools.chain.from_iterable(line_set[1:] for line_set in line_sets))

        if line_sets[0][0].startswith(b','):
            line_sets[0][0] = self._strip_indices([line_sets[0][0]])[0]
            lines = self._strip_indices(lines)

        combined = [line_sets[0][0]] + lines

        return [b'\n'.join(combined)]

    @classmethod
    def _strip_indices(cls, lines):
        return [line.split(b',', 1)[1] for line in lines]
