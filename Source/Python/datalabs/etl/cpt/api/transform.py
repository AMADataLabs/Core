""" CPT ETL Transformer classes """
from   enum import Enum
from   dataclasses import dataclass
from   datetime import datetime, date
import hashlib
import logging
import re

import pandas

from   datalabs.etl.csv import CSVReaderMixin, CSVWriterMixin
from   datalabs.parameter import add_schema
from   datalabs.task import Task

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@dataclass
class ReleaseSchedule:
    type: str
    publish_date: str
    effective_date: str


class ReleaseTypePrefix(Enum):
    NON_PLA = None
    PLA = 'PLA-'


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ReleasesTransformerParameters:
    execution_time: str


class ReleasesTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = ReleasesTransformerParameters

    def run(self):
        code_history, release_schedules, distribution_releases \
            = [self._csv_to_dataframe(datum) for datum in self._data]

        release_schedules = self._convert_months_to_integers(release_schedules)

        releases = self._generate_release_table(code_history, release_schedules)

        releases.distribution_available[releases.id.isin(distribution_releases.id)] = True

        return [self._dataframe_to_csv(releases)]

    @classmethod
    def _convert_months_to_integers(cls, release_schedules):
        release_schedules.publish_day = release_schedules.publish_day.astype(int)

        release_schedules.effective_day = release_schedules.effective_day.astype(int)

        return release_schedules

    @classmethod
    def _generate_release_table(cls, code_history, release_schedules):
        non_pla_effective_dates, pla_effective_dates = cls._get_unique_dates_from_history(code_history)

        non_pla_releases = cls._generate_releases(non_pla_effective_dates, release_schedules, ReleaseTypePrefix.NON_PLA)
        pla_releases = cls._generate_releases(pla_effective_dates, release_schedules, ReleaseTypePrefix.PLA)
        releases = pandas.concat([non_pla_releases, pla_releases])

        return releases.sort_values("effective_date", ignore_index=True).drop_duplicates()

    @classmethod
    def _get_unique_dates_from_history(cls, code_history: pandas.DataFrame):
        non_pla_dates = None
        pla_dates = None
        history = code_history[['date', 'cpt_code', 'change_type']].rename(
            columns=dict(date='release', cpt_code='code', change_type='change')
        )
        history = history.loc[history.change == 'ADDED']
        history = history.loc[~history.release.str.startswith('Pre')]

        non_pla_dates = history.loc[~history.code.str.endswith('U', na=False)].release.unique()
        pla_dates = history.loc[history.code.str.endswith('U', na=False)].release.unique()

        return (
            [datetime.strptime(d, '%Y%m%d').date() for d in non_pla_dates],
            [datetime.strptime(d, '%Y%m%d').date() for d in pla_dates]
        )

    @classmethod
    def _generate_releases(cls, effective_dates, release_schedules, type_prefix):
        release_types = [cls._get_release_type(d, release_schedules, type_prefix) for d in effective_dates]

        publish_dates = [cls._get_publish_date(d, release_schedules, type_prefix) for d in effective_dates]

        ids = [cls._generate_release_id(t, p, e) for t, p, e in zip(release_types, publish_dates, effective_dates)]

        return pandas.DataFrame(
            dict(
                type=release_types,
                publish_date=publish_dates,
                effective_date=effective_dates,
                id=ids,
                distribution_available=False
            )
        )

    @classmethod
    def _get_release_type(cls, effective_date, release_schedules, type_prefix):
        release_type = "OTHER"

        candidate_schedules = cls._get_schedules_by_effective_date(effective_date, release_schedules)

        if len(candidate_schedules) > 0:
            try:
                release_type = cls._get_schedule_by_prefix(candidate_schedules, type_prefix).type.iloc[0]
            except IndexError:
                pass

        return release_type

    @classmethod
    def _get_publish_date(cls, effective_date, release_schedules, type_prefix=None):
        publish_date = effective_date

        candidate_schedules = cls._get_schedules_by_effective_date(effective_date, release_schedules)

        if len(candidate_schedules) > 0:
            try:
                release_schedule = cls._get_schedule_by_prefix(candidate_schedules, type_prefix)

                publish_date = cls._generate_publish_date(effective_date, release_schedule)
            except IndexError:
                pass

        return publish_date

    @classmethod
    def _generate_release_id(cls, release_type, publish_date, effective_date):
        suffix = str(effective_date)

        if release_type == "ANNUAL":
            suffix = str(effective_date.year)
        elif release_type.startswith("PLA-"):
            suffix = str(publish_date.year)

        return f'{release_type}-{suffix}'

    @classmethod
    def _get_schedules_by_effective_date(cls, effective_date, release_schedules):
        effective_month = effective_date.strftime("%b")
        effective_day = effective_date.day

        return release_schedules[
            (release_schedules.effective_month == effective_month) &
            (release_schedules.effective_day == effective_day)
        ]

    @classmethod
    def _get_schedule_by_prefix(cls, release_schedules, type_prefix):
        release_schedule = None

        if type_prefix == ReleaseTypePrefix.NON_PLA:
            release_schedule = release_schedules[~release_schedules.type.str.contains("-")]
        else:
            release_schedule = release_schedules[release_schedules.type.str.startswith(type_prefix.value)]

        return release_schedule

    @classmethod
    def _generate_publish_date(cls, effective_date, release_schedule):
        publish_month = datetime.strptime(release_schedule.publish_month.iloc[0], "%b").month
        publish_day = release_schedule.publish_day.iloc[0]
        publish_date = date(effective_date.year, publish_month, publish_day)

        if publish_date > effective_date:
            publish_date = date(publish_date.year-1, publish_date.month, publish_date.day)

        return publish_date


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class CodesTransformerParameters:
    execution_time: str


class CodesTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = CodesTransformerParameters

    def run(self):
        short_descriptors, pla = [self._csv_to_dataframe(datum) for datum in self._data]
        execution_date = self._parameters.execution_time.split(' ')[0]

        codes = self._generate_code_table(short_descriptors, pla, execution_date)

        return [self._dataframe_to_csv(codes)]

    @classmethod
    def _generate_code_table(cls, descriptors, pla_details, execution_date):
        codes = descriptors[['cpt_code']].rename(
            columns=dict(cpt_code='code')
        )
        codes = codes.append(
            pla_details[['pla_code']].rename(
                columns=dict(pla_code='code')
            )
        )
        codes['deleted'] = False
        codes['modified_date'] = execution_date

        return codes


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ReleaseCodeMappingTransformerParameters:
    execution_time: str


class ReleaseCodeMappingTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = ReleaseCodeMappingTransformerParameters

    def run(self):
        releases, code_history, codes, pla = [self._csv_to_dataframe(datum) for datum in self._data]

        release_code_mappings = self._generate_release_code_mapping_table(
            releases,
            code_history,
            codes,
            pla
        )

        return [self._dataframe_to_csv(release_code_mappings)]

    # pylint: disable=too-many-function-args
    @classmethod
    def _generate_release_code_mapping_table(cls, releases, code_history, codes, pla):
        non_pla_mappings = cls._generate_non_pla_release_code_mappings(code_history, codes)
        pla_mappings = cls._generate_pla_release_code_mappings(pla)

        mapping_table = non_pla_mappings.append(pla_mappings, ignore_index=True)
        mapping_table = releases.merge(mapping_table, left_on='effective_date', right_on='release')
        mapping_table.release = mapping_table.id
        mapping_table.drop_duplicates(subset='code', keep='first', inplace=True, ignore_index=True)

        mapping_table['id'] = mapping_table.apply(cls._generate_id, axis=1)

        return mapping_table[['id', 'release', 'code']]

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
    def _generate_id(cls, mapping):
        suffix = ord(mapping.code[-1])

        if 48 <= suffix <= 57:  # between '0' and '9'
            suffix = int(mapping.code[-1])

        return int(mapping.code[:-1]) * 100 + suffix


class DescriptorTransformerMixin:
    @classmethod
    def _generate_descriptor_table(cls, name, descriptors, pla_details, execution_date):
        columns = {'cpt_code': 'code', f'{name}': 'descriptor'}
        descriptor_table = descriptors.rename(columns=columns)
        descriptor_table = descriptor_table.append(
            pla_details[['pla_code', f'{name}']].rename(
                columns={'pla_code': 'code', f'{name}': 'descriptor'}
            )
        )

        descriptor_table['deleted'] = False
        descriptor_table['modified_date'] = execution_date
        descriptor_table['descriptor_spanish'] = ''
        descriptor_table['descriptor_chinese'] = ''

        return descriptor_table


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ShortDescriptorTransformerParameters:
    execution_time: str


class ShortDescriptorTransformerTask(CSVReaderMixin, CSVWriterMixin, DescriptorTransformerMixin, Task):
    PARAMETER_CLASS = ShortDescriptorTransformerParameters

    def run(self):
        short_descriptors, pla = [self._csv_to_dataframe(datum) for datum in self._data]
        execution_date = self._parameters.execution_time.split(' ')[0]

        short_descriptor_table = self._generate_descriptor_table(
            'short_descriptor',
            short_descriptors,
            pla,
            execution_date
        )

        return [self._dataframe_to_csv(short_descriptor_table)]


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class MediumDescriptorTransformerParameters:
    execution_time: str


class MediumDescriptorTransformerTask(CSVReaderMixin, CSVWriterMixin, DescriptorTransformerMixin, Task):
    PARAMETER_CLASS = MediumDescriptorTransformerParameters

    def run(self):
        medium_descriptors, pla = [self._csv_to_dataframe(datum) for datum in self._data]
        execution_date = self._parameters.execution_time.split(' ')[0]

        medium_descriptor_table = self._generate_descriptor_table(
            'medium_descriptor',
            medium_descriptors,
            pla,
            execution_date
        )

        return [self._dataframe_to_csv(medium_descriptor_table)]


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class LongDescriptorTransformerParameters:
    execution_time: str


class LongDescriptorTransformerTask(CSVReaderMixin, CSVWriterMixin, DescriptorTransformerMixin, Task):
    PARAMETER_CLASS = LongDescriptorTransformerParameters

    def run(self):
        long_descriptors, pla = [self._csv_to_dataframe(datum) for datum in self._data]
        execution_date = self._parameters.execution_time.split(' ')[0]

        long_descriptor_table = self._generate_descriptor_table(
            'long_descriptor',
            long_descriptors,
            pla,
            execution_date
        )

        return [self._dataframe_to_csv(long_descriptor_table)]


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ModifierTypeTransformerParameters:
    execution_time: str


class ModifierTypeTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = ModifierTypeTransformerParameters

    def run(self):
        modifiers, = [self._csv_to_dataframe(datum) for datum in self._data]

        modifier_type_table = self._generate_modifier_type_table(modifiers)

        return [self._dataframe_to_csv(modifier_type_table)]

    @classmethod
    def _generate_modifier_type_table(cls, modifiers):
        modifier_types = pandas.DataFrame(dict(name=modifiers.type.unique()))

        non_asc_modifier_types = modifier_types[modifier_types.name != 'Ambulatory Service Center']

        non_asc_modifier_types['id'] = non_asc_modifier_types.apply(cls._generate_id, axis=1)

        return non_asc_modifier_types

    @classmethod
    def _generate_id(cls, modifier_type):
        return int(''.join(str(ord(x)-65) for x in modifier_type['name'].replace(' ', ''))[-9:])


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ModifierTransformerParameters:
    execution_time: str


class ModifierTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = ModifierTransformerParameters

    def run(self):
        modifiers, modifier_types = [self._csv_to_dataframe(datum) for datum in self._data]
        execution_date = self._parameters.execution_time.split(' ')[0]

        modifier_table = self._generate_modifier_table(modifiers, modifier_types, execution_date)

        return [self._dataframe_to_csv(modifier_table)]

    def _generate_modifier_table(self, modifiers, modifier_types, execution_date):
        modifiers['general'] = False
        modifiers['ambulatory_service_center'] = False
        modifiers = self._dedupe_modifiers(modifiers)

        modifiers = modifiers.merge(modifier_types, left_on='type', right_on='name')
        modifiers.type = modifiers.id

        modifiers['deleted'] = False
        modifiers['modified_date'] = execution_date

        return modifiers[[
            'modifier', 'type', 'descriptor', 'ambulatory_service_center', 'general', 'deleted', 'modified_date'
        ]]

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


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ConsumerDescriptorTransformerParameters:
    execution_time: str


class ConsumerDescriptorTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = ConsumerDescriptorTransformerParameters

    def run(self):
        codes, consumer_descriptors = [self._csv_to_dataframe(datum) for datum in self._data]
        execution_date = self._parameters.execution_time.split(' ')[0]

        consumer_descriptor_table = self._generate_consumer_descriptor_table(
            codes,
            consumer_descriptors,
            execution_date
        )

        return [self._dataframe_to_csv(consumer_descriptor_table)]

    @classmethod
    def _generate_consumer_descriptor_table(cls, codes, descriptors, execution_date):
        columns = {'cpt_code': 'code', 'consumer_descriptor': 'descriptor'}
        descriptor_table = descriptors.rename(columns=columns)
        descriptor_table['deleted'] = False

        orphaned_codes = list(descriptor_table.code[~descriptor_table.code.isin(codes.code)])
        if len(orphaned_codes) > 0:
            LOGGER.warning('Ignoring Consumer Descriptors for the following missing codes: %s', orphaned_codes)

        descriptor_table['modified_date'] = execution_date
        descriptor_table['descriptor_spanish'] = ''
        descriptor_table['descriptor_chinese'] = ''

        return descriptor_table[descriptor_table.code.isin(codes.code)]


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ClinicianDescriptorTransformerParameters:
    execution_time: str


class ClinicianDescriptorTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = ClinicianDescriptorTransformerParameters

    def run(self):
        clinician_descriptors, = [self._csv_to_dataframe(datum) for datum in self._data]
        execution_date = self._parameters.execution_time.split(' ')[0]

        clinician_descriptor_table = self._generate_clinician_descriptor_table(clinician_descriptors, execution_date)

        return [self._dataframe_to_csv(clinician_descriptor_table)]

    @classmethod
    def _generate_clinician_descriptor_table(cls, descriptors, execution_date):
        descriptor_table = descriptors[
            ['clinician_descriptor_id', 'clinician_descriptor']
        ].rename(
            columns=dict(clinician_descriptor_id='id', clinician_descriptor='descriptor')
        )

        descriptor_table['deleted'] = False
        descriptor_table['modified_date'] = execution_date
        descriptor_table['descriptor_spanish'] = ''
        descriptor_table['descriptor_chinese'] = ''

        return descriptor_table


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ClinicianDescriptorCodeMappingTransformerParameters:
    execution_time: str


class ClinicianDescriptorCodeMappingTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = ClinicianDescriptorCodeMappingTransformerParameters

    def run(self):
        codes, clinician_descriptors = [self._csv_to_dataframe(datum) for datum in self._data]

        clinician_descriptor_code_mapping_table = self._generate_clinician_descriptor_code_mapping_table(
            codes,
            clinician_descriptors
        )

        return [self._dataframe_to_csv(clinician_descriptor_code_mapping_table)]

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


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class PLADetailsTransformerParameters:
    execution_time: str


class PLADetailsTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = PLADetailsTransformerParameters

    def run(self):
        pla, = [self._csv_to_dataframe(datum) for datum in self._data]
        execution_date = self._parameters.execution_time.split(' ')[0]

        pla_details_table = self._generate_pla_details_table(pla, execution_date)

        return [self._dataframe_to_csv(pla_details_table)]

    @classmethod
    def _generate_pla_details_table(cls, pla_details, execution_date):
        pla_details_table = pla_details[['pla_code', 'status', 'test']].rename(
            columns=dict(pla_code='code', test='test_name')
        )

        pla_details_table['modified_date'] = execution_date

        return pla_details_table


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ManufacturerTransformerParameters:
    execution_time: str


class ManufacturerTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = ManufacturerTransformerParameters

    def run(self):
        pla, = [self._csv_to_dataframe(datum) for datum in self._data]
        execution_date = self._parameters.execution_time.split(' ')[0]

        manufacturer_table = self._generate_pla_manufacturer_table(pla, execution_date)

        return [self._dataframe_to_csv(manufacturer_table)]

    @classmethod
    def _generate_pla_manufacturer_table(cls, pla_details, execution_date):
        columns = {'manufacturer': 'name'}
        manufacturer_table = pla_details[['manufacturer']].rename(columns=columns)
        manufacturer_table['deleted'] = False

        manufacturer_table = manufacturer_table.dropna()
        manufacturer_table = manufacturer_table.drop_duplicates('name')

        manufacturer_table['id'] = manufacturer_table.apply(cls._generate_id, axis=1)
        manufacturer_table['modified_date'] = execution_date

        return manufacturer_table

    @classmethod
    def _generate_id(cls, manufacturer):
        name_hash = hashlib.md5(manufacturer['name'].encode('utf-8')).hexdigest()
        prefix = ''.join(str(ord(x)-65) for x in re.sub('[^a-zA-Z0-9]', '', manufacturer['name']))[-3:]
        suffix = ''.join(str(ord(x)-48) for x in name_hash)[-6:]

        return int(prefix + suffix)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class ManufacturerCodeMappingTransformerParameters:
    execution_time: str


class ManufacturerCodeMappingTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = ManufacturerCodeMappingTransformerParameters

    def run(self):
        pla,manufacturers = [self._csv_to_dataframe(datum) for datum in self._data]

        manufacturer_code_mapping_table = self._generate_pla_manufacturer_code_mapping_table(pla, manufacturers)

        return [self._dataframe_to_csv(manufacturer_code_mapping_table)]

    @classmethod
    def _generate_pla_manufacturer_code_mapping_table(cls, pla_details, manufacturers):
        columns = {'pla_code': 'code'}
        mapping_table = pla_details[['pla_code', 'manufacturer']].rename(columns=columns)

        mapping_table = mapping_table.dropna()

        mapping_table = mapping_table.merge(manufacturers, left_on='manufacturer', right_on='name')
        mapping_table.manufacturer = mapping_table.id

        return mapping_table[['code', 'manufacturer']]


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class LabTransformerParameters:
    execution_time: str


class LabTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = LabTransformerParameters

    def run(self):
        pla, = [self._csv_to_dataframe(datum) for datum in self._data]
        execution_date = self._parameters.execution_time.split(' ')[0]

        lab_table = self._generate_pla_lab_table(pla, execution_date)

        return [self._dataframe_to_csv(lab_table)]

    @classmethod
    def _generate_pla_lab_table(cls, pla_details, execution_date):
        columns = {'lab': 'name'}
        lab_table = pla_details[['lab']].rename(columns=columns)
        lab_table['deleted'] = False

        lab_table = lab_table.dropna()
        lab_table = lab_table.drop_duplicates('name')

        lab_table['id'] = lab_table.apply(cls._generate_id, axis=1)
        lab_table['modified_date'] = execution_date

        return lab_table

    @classmethod
    def _generate_id(cls, lab):
        name_hash = hashlib.md5(lab['name'].encode('utf-8')).hexdigest()
        prefix = ''.join(str(ord(x)-65) for x in re.sub('[^a-zA-Z0-9]', '', lab['name']))[-3:]
        suffix = ''.join(str(ord(x)-48) for x in name_hash)[-6:]

        return int(prefix + suffix)


@add_schema
@dataclass
# pylint: disable=too-many-instance-attributes
class LabCodeMappingTransformerParameters:
    execution_time: str


class LabCodeMappingTransformerTask(CSVReaderMixin, CSVWriterMixin, Task):
    PARAMETER_CLASS = LabCodeMappingTransformerParameters

    def run(self):
        pla, labs = [self._csv_to_dataframe(datum) for datum in self._data]

        lab_code_mapping_table = self._generate_pla_lab_code_mapping_table(pla, labs)

        return [self._dataframe_to_csv(lab_code_mapping_table)]

    @classmethod
    def _generate_pla_lab_code_mapping_table(cls, pla_details, labs):
        columns = {'pla_code': 'code'}
        mapping_table = pla_details[['pla_code', 'lab']].rename(columns=columns)

        mapping_table = mapping_table.dropna()

        mapping_table = mapping_table.merge(labs, left_on='lab', right_on='name')
        mapping_table.lab = mapping_table.id

        return mapping_table[['code', 'lab']]
