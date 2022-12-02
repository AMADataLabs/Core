"""Transformer task for running parsers on text data, converting it to fixed width text"""
from   dataclasses import dataclass
import logging

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
    formatters: str
    execution_time: str = None


class TabDelimitedToFixedWidthDescriptorTransformerTask(Task):
    PARAMETER_CLASS = TabDelimitedToFixedWidthDescriptorTransformerTaskParameters

    def run(self):
        formatters = [self._instantiate_formatter(formatter) for formatter in self._parameters.formatters.split(',')]

        formatted_data = [formatter.format(text) for formatter, text in zip(formatters, self._data)]

        return [data.encode() for data in formatted_data]

    @classmethod
    def _instantiate_formatter(cls, class_name):
        Formatter = import_plugin(class_name)  # pylint: disable=invalid-name

        return Formatter()


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class UpperCaseDescriptorTransformerTaskParameters:
    execution_time: str = None


# pylint: disable=too-many-instance-attributes
class UpperCaseDescriptorTransformerTask(Task):
    PARAMETER_CLASS = UpperCaseDescriptorTransformerTaskParameters

    def run(self):
        return [ data.decode("unicode_escape").upper().replace('\t', r'\t').encode('cp1252') for data in self._data ]
