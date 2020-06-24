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
    release_code_mapping: pandas.DataFrame
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
    manufacturer: pandas.DataFrame
    manufacturer_pla_code_mapping: pandas.DataFrame
    lab: pandas.DataFrame
    lab_pla_code_mapping: pandas.DataFrame


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
        releases = self._generate_release_table(input_data.release)
        codes = self._generate_code_table(input_data.short_descriptor)
        tables = OutputData(
            release=releases,
            code=codes,
            release_code_mapping=self._generate_release_code_mapping_table(releases, codes),
            short_descriptor=self._generate_descriptor_table('short_descriptor', input_data.short_descriptor),
            medium_descriptor=self._generate_descriptor_table('medium_descriptor', input_data.medium_descriptor),
            long_descriptor=self._generate_descriptor_table('long_descriptor', input_data.long_descriptor),
            modifier_type=self._generate_modifier_type_table(input_data.modifier),
            modifier=self._generate_modifier_table(input_data.modifier),
            consumer_descriptor=self._generate_descriptor_table('consumer_descriptor', input_data.consumer_descriptor),
            clinician_descriptor=self._generate_clinician_descriptor_table(input_data.clinician_descriptor),
            clinician_descriptor_code_mapping=self._generate_clinician_descriptor_code_mapping_table(
                input_data.clinician_descriptor
            ),
            pla_code=None,
            pla_short_descriptor=None,
            pla_medium_descriptor=None,
            pla_long_descriptor=None,
            manufacturer=None,
            manufacturer_pla_code_mapping=None,
            lab=None,
            lab_pla_code_mapping=None,
        )

        if feature.enabled('PLA'):
            tables = OutputData(
                release=tables.release,
                code=tables.code,
                release_code_mapping=tables.release_code_mapping,
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
                manufacturer=input_data.pla[['id', 'manufacturer']],
                manufacturer_pla_code_mapping=input_data.pla[
                    ['id', 'pla_code']
                ].rename(
                    columns=dict(id='id', pla_code='code')
                ),
                lab=input_data.pla[['id', 'lab_name']],
                lab_pla_code_mapping=input_data.pla[
                    ['id', 'pla_code']
                ].rename(
                    columns=dict(id='id', pla_code='code')
                )
            )

        return tables

    def _generate_release_table(self, releases):
        releases['id'] = None

        return releases

    def _generate_code_table(self, descriptors):
        codes = descriptors[['cpt_code']].rename(
            columns=dict(cpt_code='code')
        )
        codes['deleted'] = False

        return codes

    def _generate_release_code_mapping_table(self, releases, codes):
        release_ids = [None]*len(codes)  # the new release ID is unknown until it is committed to the DB

        return pandas.DataFrame(dict(release=release_ids, code=codes.code))


    def _generate_clinician_descriptor_table(self, descriptors):
        descriptor_table = self._generate_descriptor_table(
            'clinician_descriptor',
            descriptors[['clinician_descriptor_id', 'clinician_descriptor']]
        )

        return descriptor_table.rename(columns=dict(clinician_descriptor_id='id'))

    def _generate_clinician_descriptor_code_mapping_table(self, descriptors):
        mapping_table = descriptors[
            ['clinician_descriptor_id', 'cpt_code']
        ].rename(
            columns=dict(clinician_descriptor_id='clinician_descriptor', cpt_code='code')
        )
        mapping_table = mapping_table[mapping_table.code.apply(lambda x: not x.endswith('U'))]

        return mapping_table

    def _generate_descriptor_table(self, name, descriptors):
        columns = dict(cpt_code='code')
        columns[name] = 'descriptor'
        descriptor_table = descriptors.rename(columns=columns)
        descriptor_table['deleted'] = False

        return descriptor_table

    def _generate_modifier_type_table(self, modifiers):
        return pandas.DataFrame(dict(name=modifiers.type.unique()))

    def _generate_modifier_table(self, modifiers):
        modifiers = self._dedupe_modifiers(modifiers)
        modifiers['deleted'] = False

        return modifiers

    def _dedupe_modifiers(self, modifiers):
        asc_modifiers = modifiers.modifier[modifiers.type == 'Ambulatory Service Center'].tolist()
        duplicate_modifiers = modifiers[(modifiers.type == 'Category I') & modifiers.modifier.isin(asc_modifiers)]

        return modifiers.drop(index=duplicate_modifiers.index)
