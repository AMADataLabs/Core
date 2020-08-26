""" CPT ETL Transformer classes """
from   dataclasses import dataclass
from   datetime import datetime, date
import io
import logging

import numpy as np
import pandas
import sqlalchemy as sa

from   datalabs.etl.transform import TransformerTask
from   datalabs.access.orm import DatabaseTaskMixin
from   datalabs.etl.load import LoaderTask
import datalabs.etl.cpt.dbmodel as dbmodel

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
    deleted_history: pandas.DataFrame
    modifier_history: pandas.DataFrame
    code_history: pandas.DataFrame


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
    manufacturer: pandas.DataFrame
    manufacturer_pla_code_mapping: pandas.DataFrame
    lab: pandas.DataFrame
    lab_pla_code_mapping: pandas.DataFrame


@dataclass
class ReleaseSchedule:
    type: str
    publish_date: str
    effective_date: str


class CSVToRelationalTablesTransformerTask(TransformerTask, DatabaseTaskMixin):
    def _transform(self):
        _, data = zip(*self._parameters.data)  # unpack the (filename, data) tuples
        input_data = InputData(*[pandas.read_csv(io.StringIO(text)) for text in data])

        return self._generate_tables(input_data)

    def _generate_tables(self, input_data):

        codes = self._generate_code_table(input_data.short_descriptor, input_data.pla)

        tables = OutputData(
            release=self._generate_release_table(input_data.code_history),
            code=codes,
            release_code_mapping=self._generate_release_code_mapping_table(input_data.code_history, codes),
            short_descriptor=self._generate_descriptor_table(
                'short_descriptor',
                input_data.short_descriptor,
                input_data.pla
            ),
            medium_descriptor=self._generate_descriptor_table(
                'medium_descriptor',
                input_data.medium_descriptor,
                input_data.pla
            ),
            long_descriptor=self._generate_descriptor_table(
                'long_descriptor',
                input_data.long_descriptor,
                input_data.pla
            ),
            modifier_type=self._generate_modifier_type_table(input_data.modifier),
            modifier=self._generate_modifier_table(input_data.modifier),
            consumer_descriptor=self._generate_consumer_descriptor_table(codes, input_data.consumer_descriptor),
            clinician_descriptor=self._generate_clinician_descriptor_table(input_data.clinician_descriptor),
            clinician_descriptor_code_mapping=self._generate_clinician_descriptor_code_mapping_table(
                codes,
                input_data.clinician_descriptor
            ),
            pla_details=self._generate_pla_details_table(input_data.pla),
            manufacturer=self._generate_pla_manufacturer_table(input_data.pla),
            manufacturer_pla_code_mapping=self._generate_pla_manufacturer_code_mapping_table(input_data.pla),
            lab=self._generate_pla_lab_table(input_data.pla),
            lab_pla_code_mapping=self._generate_pla_lab_code_mapping_table(input_data.pla),
        )

        return tables

    @classmethod
    def _generate_release_table(cls, code_history):
        history = code_history[['date', 'cpt_code', 'change_type']].rename(
            columns=dict(date='release', cpt_code='code', change_type='change')
        )
        history = history.loc[history.change == 'ADDED']
        history = history.loc[~history.release.str.startswith('Pre')]
        history_unique = history.release.unique()
        effective_dates = [datetime.strptime(date, '%Y%m%d').date().strftime('%Y-%m-%d') for date in history_unique]

        release_schedule = cls._extract_release_schedule()
        release_types = [cls._generate_release_type(datetime.strptime(date, '%Y%m%d'), release_schedule)
                         for date in history_unique]
        publish_dates = [cls._generate_release_publish_date(datetime.strptime(date, '%Y%m%d'), release_schedule)
                         for date in history_unique]

        releases = pandas.DataFrame(
            {'publish_date': publish_dates, 'effective_date': effective_dates, 'type': release_types})

        releases.reset_index(drop=True)

        return history

    def _extract_release_schedule(self):
        with self._get_database(self._parameters.database) as database:
            release_types = database.session.query(dbmodel.ReleaseType).all()
            release_schedule = {}

            for row in release_types:
                if row.type != 'PLA-Q4':  # Explicitly skip PLA-Q4 for now since it clashes with ANNUAL
                    release_schedule[f'{row.effective_day}-{row.effective_month}'] = ReleaseSchedule(
                        type=row.type,
                        publish_date=f'{row.publish_day}-{row.publish_month}',
                        effective_date=f'{row.effective_day}-{row.effective_month}'
                    )

        return release_schedule

    @classmethod
    def _generate_release_type(cls, release_date, release_schedule):
        release_date_for_lookup = date(1900, release_date.month, release_date.day)
        types = {dates[1]: type for type, dates in release_schedule.items()}

        date_type = types.get(release_date_for_lookup, 'OTHER')

        return date_type

    @classmethod
    def _generate_release_publish_date(cls, release_date, release_schedule):
        release_date_for_lookup = date(1900, release_date.month, release_date.day)

        publish_date = {effective_dates: publish_dates for publish_dates, effective_dates in release_schedule.values()}

        date_type = publish_date.get(release_date_for_lookup, release_date)
        date_type = date(release_date.year, date_type.month, date_type.day).strftime('%Y-%m-%d')

        return date_type

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
    def _generate_release_code_mapping_table(cls, code_history, codes):
        mapping_table = code_history[['date', 'cpt_code', 'change_type']].rename(
            columns=dict(date='release', cpt_code='code', change_type='change')
        )

        mapping_table = mapping_table.loc[mapping_table.code.isin(codes.code)]
        mapping_table = mapping_table.loc[mapping_table.change == 'ADDED']
        mapping_table = mapping_table.loc[~mapping_table.release.str.startswith('Pre')]

        mapping_table.release = mapping_table.release.apply(
            lambda x: datetime.strptime(x, '%Y%m%d').strftime('%Y-%m-%d'))

        mapping_table = mapping_table.drop(columns=['change'])
        mapping_table.drop_duplicates(subset='code', keep='last', inplace=True)
        mapping_table.reset_index(drop=True, inplace=True)

        return mapping_table

    @classmethod
    def _generate_descriptor_table(cls, name, descriptors, pla_details):
        columns = {'cpt_code': 'code', f'{name}': 'descriptor'}
        descriptor_table = descriptors.rename(columns=columns)
        descriptor_table = descriptor_table.append(
            pla_details[['pla_code', f'{name}']].rename(
                columns={'pla_code': 'code', f'{name}': 'descriptor'}
            )
        )
        descriptor_table['deleted'] = False

        return descriptor_table

    @classmethod
    def _generate_consumer_descriptor_table(cls, codes, descriptors):
        columns = {'cpt_code': 'code', 'consumer_descriptor': 'descriptor'}
        descriptor_table = descriptors.rename(columns=columns)
        descriptor_table['deleted'] = False

        orphaned_codes = list(descriptor_table.code[~descriptor_table.code.isin(codes.code)])
        if len(orphaned_codes) > 0:
            LOGGER.warn('Ignoring Consumer Descriptors for the following missing codes: %s', orphaned_codes)

        return descriptor_table[descriptor_table.code.isin(codes.code)]

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
    def _generate_clinician_descriptor_code_mapping_table(cls, codes, descriptors):
        mapping_table = descriptors[
            ['clinician_descriptor_id', 'cpt_code']
        ].rename(
            columns=dict(clinician_descriptor_id='clinician_descriptor', cpt_code='code')
        )

        orphaned_codes = list(mapping_table.code[~mapping_table.code.isin(codes.code)])
        if len(orphaned_codes) > 0:
            LOGGER.warn('Ignoring Clinician Descriptor mappings for the following missing codes: %s', orphaned_codes)

        return mapping_table[mapping_table.code.isin(codes.code)]

    @classmethod
    def _generate_modifier_type_table(cls, modifiers):
        modifier_types = pandas.DataFrame(dict(name=modifiers.type.unique()))

        return modifier_types[modifier_types.name != 'Ambulatory Service Center']

    def _generate_modifier_table(self, modifiers):
        modifiers['general'] = False
        modifiers['ambulatory_service_center'] = False
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
    def _generate_pla_manufacturer_table(cls, pla_details):
        columns = {'manufacturer': 'name'}
        manufacturer_table = pla_details[['manufacturer']].rename(columns=columns)
        manufacturer_table['deleted'] = False

        manufacturer_table = manufacturer_table.dropna()
        manufacturer_table = manufacturer_table.drop_duplicates('name')

        return manufacturer_table

    @classmethod
    def _generate_pla_manufacturer_code_mapping_table(cls, pla_details):
        columns = {'pla_code': 'code'}
        mapping_table = pla_details[['pla_code', 'manufacturer']].rename(columns=columns)

        mapping_table = mapping_table.dropna()

        return mapping_table

    @classmethod
    def _generate_pla_lab_table(cls, pla_details):
        columns = {'lab': 'name'}
        lab_table = pla_details[['lab']].rename(columns=columns)
        lab_table['deleted'] = False

        lab_table = lab_table.dropna()
        lab_table = lab_table.drop_duplicates('name')

        return lab_table

    @classmethod
    def _generate_pla_lab_code_mapping_table(cls, pla_details):
        columns = {'pla_code': 'code'}
        mapping_table = pla_details[['pla_code', 'lab']].rename(columns=columns)

        mapping_table = mapping_table.dropna()

        return mapping_table

    @classmethod
    def _dedupe_modifiers(cls, modifiers):
        asc_modifiers = modifiers.modifier[modifiers.type == 'Ambulatory Service Center'].tolist()
        general_modifiers = modifiers.modifier[modifiers.type == 'Category I'].tolist()
        general_asc_modifiers = modifiers[(modifiers.type == 'Ambulatory Service Center')
                                          & modifiers.modifier.isin(general_modifiers)]
        duplicate_modifiers = modifiers[(modifiers.type == 'Category I') & modifiers.modifier.isin(asc_modifiers)]

        modifiers.loc[modifiers.modifier.isin(general_asc_modifiers), 'general'] = True
        modifiers.loc[modifiers.modifier.isin(asc_modifiers), 'type'] = 'Category I'
        modifiers.loc[modifiers.modifier.isin(asc_modifiers), 'ambulatory_service_center'] = True
        modifiers.loc[modifiers.modifier.isin(general_modifiers), 'general'] = True

        return modifiers.drop(index=duplicate_modifiers.index)
