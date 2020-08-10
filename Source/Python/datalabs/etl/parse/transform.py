""" Transformer task for running parsers on text data, converting it to CSVs. """
import logging

from   datalabs.etl.transform import TransformerTask
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class ParseToCSVTransformerTask(TransformerTask):
    def _transform(self):
        LOGGER.debug('Data to transform: %s', self._parameters.data)
        _, data = zip(*self._parameters.data)  # unpack the list of (filename, data) tuples
        parsers = self._instantiate_parsers()
        transformed_data = []

        parsed_data = [parser.parse(text) for parser, text in zip(parsers, data)]

        for datum in parsed_data:
            if hasattr(datum, 'to_csv'):
                transformed_data.append(datum.to_csv(index=False))
            else:
                transformed_data.append(str(datum))

        return transformed_data

    def _instantiate_parsers(self):
        parser_classes = self._parameters.variables['PARSERS'].split(',')

        for parser_class in parser_classes:
            yield self._instantiate_parser(parser_class)

    @classmethod
    def _instantiate_parser(cls, class_name):
        Parser = import_plugin(class_name)  # pylint: disable=invalid-name

        return Parser()
