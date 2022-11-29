"""Transformer task for running parsers on text data, converting it to fixed width text"""
from   dataclasses import dataclass
import logging

from   datalabs.etl.csv import CSVWriterMixin
from   datalabs.plugin import import_plugin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class TabDelimitedToFixedWidthDescriptorTransformerTaskParameters:
    parsers: str
    execution_time: str = None


class TabDelimitedToFixedWidthDescriptorTransformerTask(CSVWriterMixin, Task):
    PARAMETER_CLASS = TabDelimitedToFixedWidthDescriptorTransformerTaskParameters

    def run(self):

        parsers = [self._instantiate_parser(parser) for parser in self._parameters.parsers.split(',')]
        parsed_data = [parser.format(text) for parser, text in zip(parsers, self._data)]

        return [self._dataframe_to_text(data) for data in parsed_data]


    @classmethod
    def _instantiate_parser(cls, class_name):
        Parser = import_plugin(class_name)  # pylint: disable=invalid-name

        return Parser()
