""" CPT ETL Transformer classes """
from dataclasses import dataclass
import io
import logging

import pandas

import datalabs.feature as feature
from datalabs.plugin import import_plugin
from datalabs.etl.transform import Transformer

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@dataclass
class InputData:
    release: pandas.DataFrame
    short_descriptor: pandas.DataFrame
    medium_descriptor: pandas.DataFrame
    long_descriptor: pandas.DataFrame
    modifier: pandas.DataFrame
    consumer_descriptor: pandas.DataFrame
    clinician_descriptor: pandas.DataFrame
    pla: pandas.DataFrame


@dataclass
class OutputData:
    release: pandas.DataFrame
    code: pandas.DataFrame
    short_descriptor: pandas.DataFrame
    medium_descriptor: pandas.DataFrame
    long_descriptor: pandas.DataFrame
    modifier_type: pandas.DataFrame
    modifier: pandas.DataFrame
    consumer_descriptor: pandas.DataFrame
    clinician_descriptor: pandas.DataFrame
    clinician_descriptor_code_mapping: pandas.DataFrame
    pla_code: pandas.DataFrame
    pla_short_descriptor: pandas.DataFrame
    pla_long_descriptor: pandas.DataFrame
    pla_medium_descriptor: pandas.DataFrame
    pla_manufacturer: pandas.DataFrame
    pla_manufacturer_code_mapping: pandas.DataFrame
    pla_lab: pandas.DataFrame
    pla_lab_code_mapping: pandas.DataFrame


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
        if not feature.enabled('PLA'):
            data.append('DUMMY')
        input_data = InputData(*[pandas.read_csv(io.StringIO(text)) for text in data])

        return self._generate_tables(input_data)

    def _generate_tables(self, input_data):
        modifier_types = pandas.DataFrame(dict(name=input_data.modifier['type'].unique()))
        modifiers = self._dedupe_modifiers(input_data.modifier)
        codes = input_data.short_descriptor[['cpt_code']].rename(
            columns=dict(cpt_code='code')
        )
        codes['deleted'] = False

        tables = OutputData(
            release=input_data.release,
            code=input_data.short_descriptor[['cpt_code']].rename(
                columns=dict(cpt_code='code')
            ),
            short_descriptor=input_data.short_descriptor.rename(
                columns=dict(cpt_code='code', short_descriptor='descriptor')
            ),
            medium_descriptor=input_data.medium_descriptor.rename(
                columns=dict(cpt_code='code', medium_descriptor='descriptor')
            ),
            long_descriptor=input_data.long_descriptor.rename(
                columns=dict(cpt_code='code', long_descriptor='descriptor')
            ),
            modifier_type=modifier_types,
            modifier=modifiers,
            consumer_descriptor=input_data.consumer_descriptor[['cpt_code', 'consumer_descriptor']].rename(
                columns=dict(cpt_code='code', consumer_descriptor='descriptor')
            ),
            clinician_descriptor=input_data.clinician_descriptor[
                ['clinician_descriptor_id', 'clinician_descriptor']].rename(
                columns=dict(clinician_descriptor_id='id', clinician_descriptor='descriptor')
            ),
            clinician_descriptor_code_mapping=input_data.clinician_descriptor[
                ['clinician_descriptor_id', 'cpt_code']
            ].rename(
                columns=dict(clinician_descriptor_id='clinician_descriptor', cpt_code='code')
            ),
            pla_code=None,
            pla_short_descriptor=None,
            pla_medium_descriptor=None,
            pla_long_descriptor=None,
            pla_manufacturer=None,
            pla_manufacturer_code_mapping=None,
            pla_lab=None,
            pla_lab_code_mapping=None,
        )

        if feature.enabled('PLA'):
            tables = OutputData(
                code=tables.code,
                short_descriptor=tables.short_descriptor,
                medium_descriptor=tables.medium_descriptor,
                long_descriptor=tables.long_descriptor,
                modifier_type=tables.modifier_type,
                modifier=tables.modifier,
                consumer_descriptor=tables.consumer_descriptor,
                clinician_descriptor=tables.clinician_descriptor,
                clinician_descriptor_code_mapping=tables.clinician_descriptor_code_mapping,
                pla_code=input_data.pla[
                    ['pla_code', 'status', 'test']
                ].rename(
                    columns=dict(pla_code='code', status='status', test='test_name')
                ),
                pla_short_descriptor=input_data.pla[
                    ['pla_code', 'short_descriptor']
                ].rename(
                    columns=dict(pla_code='code', short_descriptor='descriptor')
                ),
                pla_medium_descriptor=input_data.pla[
                    ['pla_code', 'medium_descriptor']
                ].rename(
                    columns=dict(pla_code='code', medium_descriptor='descriptor')
                ),
                pla_long_descriptor=input_data.pla[
                    ['pla_code', 'long_descriptor']
                ].rename(
                    columns=dict(pla_code='code', long_descriptor='descriptor')
                ),
                pla_manufacturer=input_data.pla[['id', 'manufacturer']],
                pla_manufacturer_code_mapping=input_data.pla[
                    ['id', 'pla_code']
                ].rename(
                    columns=dict(id='id', pla_code='code')
                ),
                pla_lab=input_data.pla[['id', 'lab_name']],
                pla_lab_code_mapping=input_data.pla[
                    ['id', 'pla_code']
                ].rename(
                    columns=dict(id='id', pla_code='code')
                )
            )

        return tables

    def _dedupe_modifiers(self, modifiers):
        asc_modifiers = modifiers.modifier[modifiers.type == 'Ambulatory Service Center'].tolist()
        duplicate_modifiers = modifiers[(modifiers.type == 'Category I') & modifiers.modifier.isin(asc_modifiers)]

        return modifiers.drop(index=duplicate_modifiers.index)
