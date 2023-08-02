""" DataFrame manipulation transformers. """
from   dataclasses import dataclass
from   datetime import datetime
from   io import BytesIO
import itertools
import json
import logging

import numpy
import pandas

from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class SplitTransformerParameters:
    count: str
    execution_time: str = None


class SplitTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = SplitTransformerParameters

    def run(self):
        count = int(self._parameters.count)
        datasets = [self._csv_to_dataframe(data) for data in self._data]
        split_datasets = []

        for dataset in datasets:
            split_datasets += numpy.array_split(dataset, count)

        return [self._dataframe_to_csv(dataset) for dataset in split_datasets]


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ConcatenateTransformerParameters:
    execution_time: str = None


class ConcatenateTransformerTask(Task):
    PARAMETER_CLASS = ConcatenateTransformerParameters

    def run(self):
        line_sets = [data.strip().split(b'\n') for data in self._data]
        lines = list(itertools.chain.from_iterable(line_set[1:] for line_set in line_sets))

        if line_sets[0][0].startswith(b','):
            line_sets[0][0] = self._strip_indices([line_sets[0][0]])[0]
            lines = self._strip_indices(lines)

        combined = [line_sets[0][0]] + lines

        return [b'\n'.join(combined)]

    @classmethod
    def _strip_indices(cls, lines):
        return [line.split(b',', 1)[1] for line in lines]


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class DateFormatTransformerParameters:
    columns: str
    input_format: str = None
    separator: str = None
    execution_time: str = None


class DateFormatTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = DateFormatTransformerParameters

    def run(self):
        separator = self._parameters.separator if self._parameters.separator else ","
        columns = [column.strip() for column in self._parameters.columns.split(',')]
        datasets = [self._csv_to_dataframe(data, sep=separator) for data in self._data]

        reformatted_datasets = [self._reformat_dates(d, columns, self._parameters.input_format) for d in datasets]

        return [self._dataframe_to_csv(dataset, sep=separator) for dataset in reformatted_datasets]

    @classmethod
    def _reformat_dates(cls, dataset, columns, input_format):
        for column in columns:
            cls._reformat_date_column(dataset, column, input_format)

        return dataset

    @classmethod
    def _reformat_date_column(cls, dataset, column, input_format):
        condition = ~dataset[column].isna()

        if column in dataset.columns:
            dataset.loc[condition, column] = dataset.loc[condition, column].apply(
                lambda x: cls._reformat_date(x, input_format)
            )

    @classmethod
    def _reformat_date(cls, datestamp, input_format):
        '''Parse a datestamp using the input format, and return an ISO-8601 datestamp.'''
        date = datetime.strptime(datestamp, input_format)

        return date.strftime("%Y-%M-%d")