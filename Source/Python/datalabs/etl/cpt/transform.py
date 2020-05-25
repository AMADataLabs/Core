""" CPT ETL Transformer classes """
from   dataclasses import dataclass
import io
import logging

import pandas

from   datalabs.plugin import import_plugin
from   datalabs.etl.transform import Transformer

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@dataclass
class InputData:
    short_descriptor: pandas.DataFrame
    medium_descriptor: pandas.DataFrame
    long_descriptor: pandas.DataFrame
    modifier: pandas.DataFrame
    clinician_descriptor: pandas.DataFrame
    consumer_descriptor: pandas.DataFrame


class CPTFileToCSVTransformer(Transformer):
    def transform(self, data):
        LOGGER.debug('Data to transform: %s', data)
        parsers = self._instantiate_parsers()

        parsed_data = [parser.parse(text) for parser, text in zip(parsers, data)]

        return [datum.to_csv(index=False) for datum in parsed_data]

    def _instantiate_parsers(self):
        parser_classes = self._configuration['PARSERS'].split(',')

        for parser_class in parser_classes:
            yield self._instantiate_parser(parser_class)

    @classmethod
    def _instantiate_parser(cls, class_name):
        Parser = import_plugin(class_name)  # pylint: disable=invalid-name

        return Parser()


class CSVToRelationalTablesTransformer(Transformer):
    def transform(self, data):
        input_data = InputData(*[pandas.read_csv(io.StringIO(text)) for text in data])

        return self._generate_tables(input_data)

    def _generate_tables(self, input_data):
        return (
            input_data.short_descriptor[['cpt_code']].rename(
                columns=dict(cpt_code='code')
            ),
            input_data.short_descriptor.rename(
                columns=dict(cpt_code='code', short_descriptor='descriptor')
            ),
            input_data.medium_descriptor.rename(
                columns=dict(cpt_code='code', medium_descriptor='descriptor')
            ),
            input_data.long_descriptor.rename(
                columns=dict(cpt_code='code', long_descriptor='descriptor')
            ),
            input_data.consumer_descriptor[['cpt_code', 'consumer_descriptor']].rename(
                columns=dict(cpt_code='code', consumer_descriptor='descriptor')
            ),
            input_data.clinician_descriptor[['clinician_descriptor_id', 'clinician_descriptor']].rename(
                columns=dict(clinician_descriptor_id='id', clinician_descriptor='descriptor')
            ),
            input_data.clinician_descriptor[
                ['clinician_descriptor_id', 'cpt_code']
            ].rename(
                columns=dict(clinician_descriptor_id='clinician_descriptor', cpt_code='code')
            )
        )
