""" More code that will no longer be used soon """
# pylint: disable=no-name-in-module,import-error,wildcard-import,undefined-variable,protected-access,unused-import,too-many-instance-attributes,logging-fstring-interpolation,unnecessary-lambda,abstract-class-instantiated,logging-format-interpolation,no-member,trailing-newlines,trailing-whitespace

from dataclasses import dataclass
from datetime import datetime
import logging
import os
from dateutil.relativedelta import relativedelta
import pandas as pd

from datalabs.access.aims import AIMS
from datalabs.analysis.humach.survey.archive import HumachResultsArchive
from datalabs.analysis.vertical_trail.physician_contact.archive import VTPhysicianContactArchive

from filter_bad_phones import get_good_bad_phones  # /Sandbox/CommonCode/filter_bad_phones.py
import settings

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@dataclass
class AIMSData:
    no_contacts: pd.DataFrame = pd.DataFrame()
    pe_descriptions: pd.DataFrame = pd.DataFrame()


# pylint: disable=too-many-statements
class HumachSampleGenerator:
    def __init__(
            self,
            archive: HumachResultsArchive = None,
            vt_archive: VTPhysicianContactArchive = None,
            survey_type='STANDARD',
            custom_exclusion_file_list=None):
        self._survey_type = survey_type
        self._target_sample_vars = []

        self._sample_size = None
        self._save_dir = None
        self._archive = archive
        self._vt_archive = vt_archive
        self._ppd_filename = None
        self._custom_exclusion_file_list = custom_exclusion_file_list

        """ Exclusion time periods """
        self._months_me_block = None
        self._months_phone_block = None

        """ Date """
        self._today_date = datetime.now().date()
        self._survey_date = self._today_date + relativedelta(months=1)

        self.source_filename_map = {
            'MF': 'Masterfile_Random_Sample',
            'VT': 'VT_VerificationSample'
        }
        self.survey_type_filename_map = {
            'VERTICAL_TRAIL': 'VT_Verification_Sample',
            'STANDARD': 'Masterfile_Random_Sample',
            'VALIDATION': 'Validation_Sample'
        }

    def create_masterfile_random_sample(self, include_me_list=None, exclude_me_list=None, filter_recent_mes=True):
        LOGGER.info('SETTING VARIABLES AND CONNECTIONS')
        self._load_environment_variables()
        LOGGER.info('CREATING POPULATION DATA')
        population_data = self._get_population_data(
            include_me_list=include_me_list,
            filter_recent_mes=filter_recent_mes
        )
        if exclude_me_list is not None:
            LOGGER.info(f'REMOVING {len(exclude_me_list)} FROM POPULATION BASED ON EXCLUSION LIST')
            population_data = population_data[~population_data['ME'].isin(exclude_me_list)]
        LOGGER.info(f'POPULATION SIZE - {str(len(population_data))}')
        self._make_sample(population_data, size=self._sample_size, source='MF')

    def create_vertical_trail_verification_sample(self):
        LOGGER.info('SETTING VARIABLES AND CONNECTIONS')
        self._load_environment_variables()
        LOGGER.info('GETTING LATEST VERTICAL TRAIL RESULTS')
        latest_result_sample_id = self._vt_archive.get_latest_results_sample_id()
        LOGGER.info('LATEST SAMPLE ID - %s', latest_result_sample_id)
        latest_result_data = self._vt_archive.get_results_for_sample_id(latest_result_sample_id)
        LOGGER.info('LATEST SAMPLE RESULTS SIZE - %d', len(latest_result_data))
        LOGGER.info('CREATING POPULATION DATA')
        population_data = self._get_vertical_trail_verification_population_data(result_data=latest_result_data)
        LOGGER.info('CREATING SAMPLE')
        self._make_sample(
            population_data=population_data,
            size=len(population_data),
            source='VT',
            reference_sample_id=latest_result_sample_id
        )

    def _get_vertical_trail_results(self, sample_ids: list = None) -> pd.DataFrame:
        if sample_ids is None:
            sample_ids = [self._vt_archive.get_latest_sample_id()]
        if not isinstance(sample_ids, (list, set)):
            sample_ids = [sample_ids]

        data = self._vt_archive.get_results_for_sample_ids(sample_ids)
        return data

    def _get_vertical_trail_verification_population_data(self, result_data: pd.DataFrame):
        ppd = self._load_ppd()
        if 'TOP_CD' not in ppd.columns:
            print(ppd.columns.values)
            raise ValueError('TOP_CD (used to filter to DPC) not found in columns.')
        aims_data = self._load_aims_data()

        result_data.columns = ['VT_' + col.upper() for col in result_data.columns.values]
        data = ppd.merge(result_data, left_on='ME', right_on='VT_ME', how='inner')

        data = self._prepare_vertical_trail_verification_population_data(data, aims_data=aims_data)
        return data

    def _load_environment_variables(self):
        self._save_dir = os.environ.get('SAVE_DIR')
        self._ppd_filename = os.environ.get('EXPANDED_PPD_FILE')
        self._archive = HumachResultsArchive(os.environ.get('ARCHIVE_DB_PATH'))
        self._vt_archive = VTPhysicianContactArchive(os.environ.get('ARCHIVE_DB_PATH'))
        self._target_sample_vars = self._archive.table_columns.samples
        self._months_me_block = os.environ.get('MONTHS_ME_BLOCK')
        self._months_phone_block = os.environ.get('MONTHS_PHONE_BLOCK')
        self._sample_size = os.environ.get(f'SAMPLE_SIZE_{self._survey_type}')

    def _get_population_data(self, include_me_list=None, filter_recent_mes=True):
        ppd = self._load_ppd()
        if include_me_list is not None:
            LOGGER.info(f'Filtering PPD to list of {len(include_me_list)} values')
            ppd['ME'] = ppd['ME'].astype(str).apply(lambda x: ('00000000'+x)[-11:])
            include_me_list = include_me_list.astype(str).apply(lambda x: ('00000000'+x)[-11:])
            ppd = ppd[ppd['ME'].isin(include_me_list)]
            ppd_len = len(ppd)
            if ppd_len < int(self._sample_size):
                print(ppd_len)
                raise ValueError(
                    'PPD filtered below sample size. Please check include_me_list, make sure it contains leading 0s.'
                )
        aims_data = self._load_aims_data()

        data = self._prepare_population_data(data=ppd, aims_data=aims_data, filter_recent_mes=filter_recent_mes)
        return data

    def _make_sample(self, population_data: pd.DataFrame, size, source='MF', reference_sample_id=None):
        if size is None:
            size = len(population_data)
        LOGGER.info(f'CREATING SAMPLE - SIZE: {str(self._sample_size)}')
        sample = population_data.sample(n=min(int(size), len(population_data))).reset_index()

        sample = self._add_sample_info_columns(data=sample, source=source, reference_sample_id=reference_sample_id)
        sample = self._format_sample_columns(data=sample)

        self._save_sample_and_deliverable(sample)

    def _load_ppd(self):
        LOGGER.info(f'Loading PPD: {self._ppd_filename}')
        ppd = pd.read_csv(self._ppd_filename, dtype=str)
        return ppd

    @classmethod
    def _load_aims_data(cls):
        aims_data = AIMSData()
        with AIMS.from_environment("AIMS") as aims:
            aims_data.no_contacts = aims.get_no_contacts()
            aims_data.pe_descriptions = aims.get_pe_descriptions()
        return aims_data

    def _prepare_population_data(self, data: pd.DataFrame, aims_data: AIMSData, filter_recent_mes=True):
        LOGGER.info('Filtering to DPC')
        data = self._filter_to_dpc(data=data)
        LOGGER.info('Filtering to valid phones')
        data = self._filter_to_valid_phones(data=data)
        LOGGER.info('Filtering out no-contacts')
        data = self._filter_no_contacts(data=data, aims_data=aims_data)
        if filter_recent_mes:
            LOGGER.info('Filtering out ME numbers found in recent samples')
            data = self._filter_recent_me(data=data)
        LOGGER.info('Filtering out phone numbers found in recent samples')
        data = self._filter_recent_phones(data=data)
        if self._custom_exclusion_file_list is not None:
            LOGGER.info('Filtering out ME numbers found in custom file list')
            data = self._filter_me_from_custom_files(data=data, file_list=self._custom_exclusion_file_list)
        LOGGER.info('Adding present employment description')
        data = self._add_pe_description(data=data, aims_data=aims_data)
        return data

    def _prepare_vertical_trail_verification_population_data(self, data: pd.DataFrame, aims_data: AIMSData):
        # filter out physicians which already have phone number
        data = data[data['TELEPHONE_NUMBER'].apply(lambda x: self._isna(x))]
        data['TELEPHONE_NUMBER'] = data['VT_PHONE_NUMBER']  # replace PPD phone with VT phone
        data = data[data['TELEPHONE_NUMBER'].apply(lambda x: not self._isna(x))]  # VT results can be null
        len1 = len(data)
        LOGGER.info(f'SIZE PRE-NO_CONTACT FILTER: {len1}')
        data = self._filter_no_contacts(data=data, aims_data=aims_data)
        len2 = len(data)
        LOGGER.info(f'SIZE POST-NO_CONTACT FILTER: {len2}')
        LOGGER.info(f'FILTERED OUT {len1-len2} RECORDS')
        #data = self._filter_recent_phones(data=data)
        #data = self._filter_me_from_custom_files(data=data, file_list=self._custom_exclusion_file_list)
        data = self._add_pe_description(data=data, aims_data=aims_data)
        return data

    def _add_sample_info_columns(self, data, source='MF', reference_sample_id=None):
        latest_id = self._archive.get_latest_sample_id()
        if latest_id is None:
            latest_id = 1
        sample_id = latest_id + 1

        if reference_sample_id is not None:
            print('REFERENCE - ', reference_sample_id)
            self._archive.insert_humach_sample_reference(
                humach_sample_id=sample_id,
                other_sample_id=reference_sample_id,
                other_sample_source=source
            )

        data['SAMPLE_ID'] = sample_id
        data['ROW_ID'] = data.index + 1
        data['SURVEY_TYPE'] = self._survey_type.upper()
        data['SURVEY_MONTH'] = self._survey_date.month
        data['SURVEY_YEAR'] = self._survey_date.year
        data['SAMPLE_SOURCE'] = source

        return data

    def _format_sample_columns(self, data: pd.DataFrame):
        data.columns = [col.upper() for col in data.columns.values]  # uppercase DataFrame column names
        cols = [col.upper() for col in self._target_sample_vars]  # target sample file column names
        data.rename(columns={'PREFERRED_PHONE_COMM_ID': 'PHONE_COMM_ID'}, inplace=True)  # expected name in the DB table

        # re-orders DataFrame columns to match order specified in self._target_sample_vars
        sample = pd.DataFrame()
        for col in cols:
            sample[col] = data[col]

        return sample

    def _save_sample_and_deliverable(self, sample):
        filename = self.survey_type_filename_map[self._survey_type]
        self._load_sample_to_archive(sample)
        self._make_deliverable_sample(sample, filename=filename)

    @classmethod
    def _filter_to_dpc(cls, data: pd.DataFrame):
        data = data[data['TOP_CD'] == '020']
        return data

    @classmethod
    def _filter_to_valid_phones(cls, data: pd.DataFrame):
        data = data[~data['TELEPHONE_NUMBER'].isna()]
        _, data = get_good_bad_phones(data, phone_var_name='TELEPHONE_NUMBER')
        return data

    def _filter_no_contacts(self, data: pd.DataFrame, aims_data: AIMSData):
        data = self._filter_data(
            data=data,
            data_col='ENTITY_ID',
            filter_data=aims_data.no_contacts,
            filter_col='entity_id'
        )
        return data

    def _filter_recent_phones(self, data: pd.DataFrame):
        previous_n_months_data = self._archive.get_sample_data_past_n_months(self._months_phone_block)
        data = self._filter_data(data=data, data_col='TELEPHONE_NUMBER',
                                 filter_data=previous_n_months_data, filter_col='telephone_number')
        return data

    def _filter_recent_me(self, data: pd.DataFrame):
        previous_n_months_data = self._archive.get_sample_data_past_n_months(self._months_me_block)
        data = self._filter_data(
            data=data,
            data_col='ME',
            filter_data=previous_n_months_data,
            filter_col='me'
        )
        return data

    def _filter_me_from_custom_files(self, data, file_list):
        if file_list is not None:
            data_list = []
            for file in file_list:
                to_filter = pd.read_excel(file, dtype=str, usecols=['ME'])
                data_list.append(to_filter)
            to_filter = pd.concat(data_list)
            data = self._filter_data(
                data=data,
                data_col='ME',
                filter_data=to_filter,
                filter_col='ME'
            )
        return data

    @classmethod
    def _add_pe_description(cls, data: pd.DataFrame, aims_data: AIMSData):
        data = data.merge(aims_data.pe_descriptions, left_on='PE_CD', right_on='present_emp_cd', how='left')
        return data

    def _load_sample_to_archive(self, sample):
        self._archive.ingest_sample_data(sample)

    def _make_deliverable_sample(self, sample, filename='Masterfile_Random_Sample'):
        deliverable = sample.drop(
            columns=[
                'SURVEY_TYPE',
                'SURVEY_MONTH',
                'SURVEY_YEAR',
                'SAMPLE_SOURCE',
                'PHONE_COMM_ID',
                'ENTITY_ID',
                'POLO_COMM_ID'
            ]
        )
        sample_name = f'\\{self._today_date}_{filename}.xlsx'
        sample_save_path = self._save_dir + sample_name
        writer = pd.ExcelWriter(sample_save_path, engine='xlsxwriter')

        LOGGER.info('SAVING SAMPLE TO %s', sample_save_path)
        deliverable.to_excel(excel_writer=writer, index=None)
        writer.save()

    @classmethod
    def _filter_data(cls, data: pd.DataFrame, data_col: str, filter_data: pd.DataFrame, filter_col: str):
        return data[~data[data_col].isin(filter_data[filter_col])]

    @classmethod
    def _isna(cls, text):
        is_na = False
        if text is None or str(text).upper().strip() in ('', 'NONE', 'NAN', 'NA'):
            is_na = True
        return is_na


def make_standard_survey():
    gen = HumachSampleGenerator(survey_type='STANDARD')
    gen.create_masterfile_random_sample()


def make_validation_survey():
    gen = HumachSampleGenerator(survey_type='VALIDATION')
    gen.create_masterfile_random_sample()


def make_vertical_trail_verification_sample():
    gen = HumachSampleGenerator(survey_type='VERTICAL_TRAIL')
    gen.create_vertical_trail_verification_sample()
