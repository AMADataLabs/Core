""" CPT ETL Transformer classes """
from   enum import Enum
from   dataclasses import dataclass
from   datetime import datetime, date
import io
import logging

import pandas

from   datalabs.access.orm import Database
from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.etl.transform import TransformerTask
import datalabs.model.cpt.api as dbmodel
from   datalabs.parameter import add_schema

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ReleasesTransformerParameters:
    data: list
    execution_time: str = None


class ReleasesTransformerTask(CSVReaderMixin, CSVWriterMixin, TransformerTask):
    PARAMETER_CLASS = ReleasesTransformerParameters

    def _transform(self):
        code_history, pla, release_schedules = [self._csv_to_dataframe(datum) for datum in self._parameters.data]

        releases = self._generate_release_table(code_history, pla, release_schedules)

        return [self._dataframe_to_csv(releases)]

    @classmethod
    def _generate_release_table(cls, code_history, pla, release_schedules):
        non_pla_release = cls._generate_non_pla_releases(release_schedules, code_history)
        pla_release = cls._generate_pla_releases(release_schedules, pla)

        releases = non_pla_release.append(pla_release, ignore_index=True)
        releases = releases.drop_duplicates(ignore_index=True)

        return releases

    @classmethod
    def _generate_non_pla_releases(cls, release_schedules, code_history):
        history_unique = cls._get_unique_dates_from_history(code_history)

        effective_dates, publish_dates = cls._generate_non_pla_release_dates(release_schedules, history_unique)

        release_types = cls._generate_non_pla_release_types(release_schedules, effective_dates)

        return pandas.DataFrame(
            {'publish_date': publish_dates, 'effective_date': effective_dates, 'type': release_types})

    @classmethod
    def _generate_pla_releases(cls, release_schedules, pla_details):
        effective_dates, publish_dates = cls._generate_pla_release_dates(release_schedules, pla_details)

        release_types = cls._generate_pla_release_types(release_schedules, publish_dates)

        return pandas.DataFrame(
            {'publish_date': publish_dates, 'effective_date': effective_dates, 'type': release_types})

    @classmethod
    def _get_unique_dates_from_history(cls, code_history):
        history = code_history[['date', 'cpt_code', 'change_type']].rename(
            columns=dict(date='release', cpt_code='code', change_type='change')
        )
        history = history.loc[history.change == 'ADDED']
        history = history.loc[~history.release.str.startswith('Pre')]
        history = history.loc[~history.code.str.endswith('U', na=False)]
        history_unique = history.release.unique()

        return history_unique

    @classmethod
    def _generate_non_pla_release_dates(cls, release_schedules, history):
        effective_dates = [datetime.strptime(date, '%Y%m%d').date() for date in history]

        publish_dates = cls._generate_release_publish_dates(release_schedules, effective_dates)

        return effective_dates, publish_dates

    @classmethod
    def _generate_non_pla_release_types(cls, release_schedules, effective_dates):
        return cls._generate_release_types(release_schedules, effective_dates, ReleaseScheduleType.NON_PLA)

    @classmethod
    def _generate_pla_release_dates(cls, release_schedules, pla_details):
        pla = pla_details[['effective_date', 'published_date']].rename(
            columns=dict(published_date='publish_date')
        )
        pla_releases = pla.drop_duplicates(ignore_index=True)

        effective_dates = [
            datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z').date() for date in pla_releases.effective_date
        ]
        publish_dates = [datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z').date() for date in pla_releases.publish_date]

        return effective_dates, publish_dates

    @classmethod
    def _generate_pla_release_types(cls, release_schedules, publish_dates):
        return cls._generate_release_types(release_schedules, publish_dates, ReleaseScheduleType.PLA)

    @classmethod
    def _generate_release_publish_dates(cls, release_schedules, release_dates):
        publish_dates = []
        release_schedules = cls._generate_release_schedules_map_from_type(release_schedules, ReleaseScheduleType.NON_PLA)

        for release_date in release_dates:
            release_date_for_lookup = date(release_date.year, release_date.month, release_date.day).strftime('%-d-%b')
            default_release_schedule = ReleaseSchedule('OTHER', release_date_for_lookup, release_date_for_lookup)

            publish_date = release_schedules.get(release_date_for_lookup, default_release_schedule).publish_date
            publish_date = datetime.strptime(publish_date, '%d-%b').date()
            publish_date = date(release_date.year, publish_date.month, publish_date.day)

            if not publish_date:
                publish_date = release_date

            publish_dates.append(publish_date)

        return publish_dates

    @classmethod
    def _generate_release_types(cls, release_schedules, release_dates, schedule_type):
        release_types = []
        release_schedules = cls._generate_release_schedules_map_from_type(release_schedules, schedule_type)

        for release_date in release_dates:
            release_date_for_lookup = date(1900, release_date.month, release_date.day).strftime('%-d-%b')
            default_release_schedule = ReleaseSchedule('OTHER', release_date_for_lookup, release_date_for_lookup)
            release_types.append(release_schedules.get(release_date_for_lookup, default_release_schedule).type)

        return release_types

    @classmethod
    def _generate_release_schedules_map_from_type(cls, release_schedules, schedule_type):
        release_schedules_map = {}

        for release_type in release_schedules.type:
            if release_type.startswith(schedule_type.value):
                release_schedule = release_schedules[release_schedules.type == release_type]
                effective_date = f'{release_schedule.effective_day.iloc[0]}-{release_schedule.effective_month.iloc[0]}'
                publish_date = f'{release_schedule.publish_day.iloc[0]}-{release_schedule.publish_month.iloc[0]}'

                release_schedules_map[effective_date] = ReleaseSchedule(
                    type=release_type,
                    publish_date=publish_date,
                    effective_date=effective_date
                )

        return release_schedules_map








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


class ReleaseScheduleType(Enum):
    NON_PLA = 'ANNUAL'
    PLA = 'PLA'


class CSVToRelationalTableTransformerTask(TransformerTask):
    def _transform(self):
        LOGGER.debug(
            '%s parameters (sans data): %s', self.__class__.__name__,
            {key:value for key, value in self._parameters.items() if key != 'data'}
        )

        _, data = zip(*pickle.loads(self._parameters['data'][0]))  # unpack the (filename, data) tuples
        input_data = InputData(*[pandas.read_csv(io.StringIO(text)) for text in data])

        return self._generate_tables(input_data)

    def _generate_tables(self, input_data):
        codes = self._generate_code_table(input_data.short_descriptor, input_data.pla)

        tables = OutputData(
            release=self._generate_release_table(input_data.code_history, input_data.pla),
            code=codes,
            release_code_mapping=self._generate_release_code_mapping_table(
                input_data.code_history,
                codes,
                input_data.pla
            ),
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

    # pylint: disable=too-many-function-args
    @classmethod
    def _generate_release_code_mapping_table(cls, code_history, codes, pla):
        non_pla_mappings = cls._generate_non_pla_release_code_mappings(code_history, codes)
        pla_mappings = cls._generate_pla_release_code_mappings(pla)

        mapping_table = non_pla_mappings.append(pla_mappings, ignore_index=True)

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
            LOGGER.warning('Ignoring Consumer Descriptors for the following missing codes: %s', orphaned_codes)

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
            LOGGER.warning('Ignoring Clinician Descriptor mappings for the following missing codes: %s', orphaned_codes)

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
        pla_details_table = pla_details[['pla_code', 'status', 'test']].rename(
            columns=dict(pla_code='code', test='test_name')
        )

        return pla_details_table

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
    def _generate_non_pla_release_code_mappings(cls, code_history, codes):
        non_pla_mapping_table = code_history[['date', 'cpt_code', 'change_type']].rename(
            columns=dict(date='release', cpt_code='code', change_type='change')
        )
        non_pla_mapping_table = non_pla_mapping_table.loc[non_pla_mapping_table.code.isin(codes.code)]
        non_pla_mapping_table = non_pla_mapping_table.loc[non_pla_mapping_table.change == 'ADDED']
        non_pla_mapping_table = non_pla_mapping_table.loc[~non_pla_mapping_table.release.str.startswith('Pre')]
        non_pla_mapping_table = non_pla_mapping_table.loc[~non_pla_mapping_table.code.str.endswith('U')]
        non_pla_mapping_table = non_pla_mapping_table.drop(columns=['change'])
        non_pla_mapping_table.drop_duplicates(subset='code', keep='last', inplace=True)

        non_pla_mapping_table.release = non_pla_mapping_table.release.apply(
            lambda x: datetime.strptime(x, '%Y%m%d').strftime('%Y-%m-%d'))

        return non_pla_mapping_table

    @classmethod
    def _generate_pla_release_code_mappings(cls, pla_details):
        pla_mapping_table = pla_details[['effective_date', 'pla_code']].rename(
            columns=dict(effective_date='release', pla_code='code')
        )

        pla_mapping_table.release = pla_mapping_table.release.apply(
            lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d'))

        return pla_mapping_table

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

    def _get_database(self):
        Database.from_parameters(self._parameters, prefix='DATABASE_')
