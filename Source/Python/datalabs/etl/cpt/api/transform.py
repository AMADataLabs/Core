""" CPT ETL Transformer classes """
from   dataclasses import dataclass
from   datetime import datetime
import io
import logging

import pandas

from   datalabs.etl.transform import TransformerTask


logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

# pylint: disable=too-many-instance-attributes
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


# pylint: disable=too-many-instance-attributes
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
    pla_details: pandas.DataFrame
    pla_short_descriptor: pandas.DataFrame
    pla_long_descriptor: pandas.DataFrame
    pla_medium_descriptor: pandas.DataFrame
    manufacturer: pandas.DataFrame
    manufacturer_pla_code_mapping: pandas.DataFrame
    lab: pandas.DataFrame
    lab_pla_code_mapping: pandas.DataFrame
    # pla_release: pandas.DataFrame


class CSVToRelationalTablesTransformerTask(TransformerTask):
    def _transform(self):
        _, data = zip(*self._parameters.data)  # unpack the (filename, data) tuples
        input_data = InputData(*[pandas.read_csv(io.StringIO(text)) for text in data])

        return self._generate_tables(input_data)

    def _generate_tables(self, input_data):
        releases = self._generate_release_table(input_data.release)
        codes = self._generate_code_table(input_data.short_descriptor, input_data.pla)

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
            pla_details=self._generate_pla_details_table(input_data.pla),
            pla_short_descriptor=self._generate_pla_descriptor_table('short_descriptor', input_data.pla),
            pla_medium_descriptor=self._generate_pla_descriptor_table('medium_descriptor', input_data.pla),
            pla_long_descriptor=self._generate_pla_descriptor_table('long_descriptor', input_data.pla),
            manufacturer=self._generate_pla_manufacturer_table(input_data.pla),
            manufacturer_pla_code_mapping=self._generate_pla_manufacturer_code_mapping_table(input_data.pla),
            lab=self._generate_pla_lab_table(input_data.pla),
            lab_pla_code_mapping=self._generate_pla_lab_code_mapping_table(input_data.pla),
            # pla_release=self._generate_pla_release_code_mapping_table(input_data.pla)
        )

        return tables

    @classmethod
    def _generate_release_table(cls, releases):
        releases.id = None
        releases.publish_date = releases.publish_date.apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
        releases.effective_date = releases.effective_date.apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())

        return releases

    @classmethod
    def _generate_code_table(cls, descriptors, pla_details):
        codes = descriptors[['cpt_code']].rename(
            columns=dict(cpt_code='code')
        )
        codes = codes.append(
            pla_details[['pla_code']].rename(
                columns=dict(pla_code='code')
            )
        )
        codes['deleted'] = False

        return codes

    @classmethod
    def _generate_release_code_mapping_table(cls, releases, codes):
        ids = [None] * len(codes)  # Placeholder for new mapping IDs
        releases = [None] * len(codes)  # the new release ID is unknown until it is committed to the DB

        return pandas.DataFrame(dict(id=ids, release=releases, code=codes.code))

    @classmethod
    def _generate_clinician_descriptor_table(cls, descriptors):
        descriptor_table = descriptors[
            ['clinician_descriptor_id', 'clinician_descriptor']
        ].rename(
            columns=dict(clinician_descriptor_id='id', clinician_descriptor='descriptor')
        )
        descriptor_table['deleted'] = False

        return descriptor_table

    @classmethod
    def _generate_clinician_descriptor_code_mapping_table(cls, descriptors):
        mapping_table = descriptors[
            ['clinician_descriptor_id', 'cpt_code']
        ].rename(
            columns=dict(clinician_descriptor_id='clinician_descriptor', cpt_code='code')
        )
        mapping_table = mapping_table[mapping_table.code.apply(lambda x: not x.endswith('U'))]

        return mapping_table

    @classmethod
    def _generate_descriptor_table(cls, name, descriptors):
        columns = {'cpt_code': 'code', f'{name}': 'descriptor'}
        descriptor_table = descriptors.rename(columns=columns)
        descriptor_table['deleted'] = False

        return descriptor_table[descriptor_table.code.apply(lambda x: not x.endswith('U'))]

    @classmethod
    def _generate_modifier_type_table(cls, modifiers):
        return pandas.DataFrame(dict(name=modifiers.type.unique()))

    def _generate_modifier_table(self, modifiers):
        modifiers = self._dedupe_modifiers(modifiers)
        modifiers['deleted'] = False

        return modifiers

    @classmethod
    def _generate_pla_details_table(cls, pla_details):
        codes = pla_details[['pla_code', 'status', 'test']].rename(
            columns=dict(pla_code='code', test='test_name')
        )
        codes['deleted'] = False

        return codes

    @classmethod
    def _generate_pla_descriptor_table(cls, name, pla_details):
        columns = {'pla_code': 'code', f'{name}': 'descriptor'}
        descriptor_table = pla_details[['pla_code', f'{name}']].rename(columns=columns)
        descriptor_table['deleted'] = False

        return descriptor_table

    @classmethod
    def _generate_pla_manufacturer_table(cls, pla_details):
        columns = {'manufacturer': 'name'}
        manufacturer_table = pla_details[['manufacturer']].rename(columns=columns)
        manufacturer_table['deleted'] = False

        return manufacturer_table

    @classmethod
    def _generate_pla_manufacturer_code_mapping_table(cls, pla_details):
        columns = {'pla_code': 'code'}
        mapping_table = pla_details[['pla_code', 'manufacturer']].rename(columns=columns)

        return mapping_table

    @classmethod
    def _generate_pla_lab_table(cls, pla_details):
        columns = {'lab': 'name'}
        lab_table = pla_details[['lab']].rename(columns=columns)
        lab_table['deleted'] = False

        return lab_table

    @classmethod
    def _generate_pla_lab_code_mapping_table(cls, pla_details):
        columns = {'pla_code': 'code'}
        mapping_table = pla_details[['pla_code', 'lab']].rename(columns=columns)

        return mapping_table

    @classmethod
    def _dedupe_modifiers(cls, modifiers):
        asc_modifiers = modifiers.modifier[modifiers.type == 'Ambulatory Service Center'].tolist()
        duplicate_modifiers = modifiers[(modifiers.type == 'Category I') & modifiers.modifier.isin(asc_modifiers)]

        return modifiers.drop(index=duplicate_modifiers.index)
