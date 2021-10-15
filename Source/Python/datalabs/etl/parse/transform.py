""" Transformer task for running parsers on text data, converting it to CSVs. """
from   dataclasses import dataclass
import logging

from   datalabs.etl.csv import CSVWriterMixin
from   datalabs.etl.transform import TransformerTask
from   datalabs.plugin import import_plugin
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ParseToCSVTransformerParameters:
    parsers: str
    data: list
    execution_time: str = None


class ParseToCSVTransformerTask(CSVWriterMixin, TransformerTask):
    PARAMETER_CLASS = ParseToCSVTransformerParameters

    def _transform(self):
        parsers = [self._instantiate_parser(parser) for parser in self._parameters.parsers.split(',')]

        parsed_data = [parser.parse(text) for parser, text in zip(parsers, self._parameters.data)]

        return [self._dataframe_to_csv(data) for data in parsed_data]

    @classmethod
    def _instantiate_parser(cls, class_name):
        Parser = import_plugin(class_name)  # pylint: disable=invalid-name

        return Parser()
