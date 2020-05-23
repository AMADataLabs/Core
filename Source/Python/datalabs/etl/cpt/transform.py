""" CPT ETL Transformer classes """
import io
import logging

from   datalabs.plugin import import_plugin
from   datalabs.etl.transform import Transformer

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class CPTFileToCSVTransformer(Transformer):
    def __init__(self, configuration):
        super().__init__(configuration)

    def transform(self, data):
        LOGGER.debug('Data to transform: %s', data)
        parsers = self._instantiate_parsers()

        parsed_data = [parser.parse(text) for parser, text in zip(parsers, data)]

        return [datum.to_csv() for datum in parsed_data]

    def _instantiate_parsers(self):
        parser_classes = self._configuration['PARSERS'].split(',')

        for parser_class in parser_classes:
            yield self._instantiate_parser(parser_class)

    def _instantiate_parser(self, class_name):
        Parser = import_plugin(class_name)  # pylint: disable=invalid-name

        return Parser()
