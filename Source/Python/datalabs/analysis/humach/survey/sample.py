import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

from datalabs.analysis.humach.survey.archive import HumachResultsArchive
from datalabs.access.aims import AIMS

from filter_bad_phones import get_good_bad_phones

import settings


class AIMSData:
    no_contacts = pd.DataFrame()
    pe_descriptions = pd.DataFrame()


class HumachSampleGenerator:
    def __init__(self, archive: HumachResultsArchive = None, survey_type: str = None):
        self._survey_type = survey_type
        self._target_sample_vars = []

        self._sample_size = None
        self._save_dir = None
        self._archive = archive
        self._ppd_filename = None

        """ Exclusion time periods """
        self._months_me_block = None
        self._months_phone_block = None

        """ Date """
        self._today_date = datetime.now().date()
        self._survey_date = self._today_date + relativedelta(months=1)

    def run(self):
        LOGGER.info('SETTING VARIABLES AND CONNECTIONS')
        self._load_environment_variables()
        LOGGER.info('CREATING POPULATION DATA')
        population_data = self._get_population_data()
        LOGGER.info('CREATING SAMPLE')
        self._make_sample(population_data, size=self._sample_size)

    def _load_environment_variables(self):
        self._save_dir = os.environ.get('SAVE_DIR')
        self._ppd_filename = os.environ.get('EXPANDED_PPD_FILE')
        self._archive = HumachResultsArchive(os.environ.get('SURVEY_DB_PATH'))
        self._target_sample_vars = self._archive.sample_cols
        self._months_me_block = os.environ.get('MONTHS_ME_BLOCK')
        self._months_phone_block = os.environ.get('MONTHS_PHONE_BLOCK')
        self._sample_size = os.environ.get('SAMPLE_SIZE')

    def _get_population_data(self):
        ppd = self._load_ppd()
        aims_data = self._load_aims_data()

        data = self._prepare_population_data(data=ppd, aims_data=aims_data)
        return data

    def _load_ppd(self):
        ppd = pd.read_csv(self._ppd_filename, dtype=str)
        return ppd

    @classmethod
    def _load_aims_data(cls):
        aims_data = AIMSData()
        with AIMS() as aims:
            aims_data.no_contacts = aims.get_no_contacts()
            aims_data.pe_descriptions = aims.get_pe_descriptions()
        return aims_data

    def _prepare_population_data(self, data: pd.DataFrame, aims_data: AIMSData):
        data = self._filter_to_dpc(data=data)
        data = self._filter_to_valid_phones(data=data)
        data = self._filter_no_contacts(data=data, aims_data=aims_data)
        data = self._filter_recent_me(data=data)
        data = self._filter_recent_phones(data=data)
        data = self._add_pe_description(data=data, aims_data=aims_data)
        return data

    def _make_sample(self, population_data: pd.DataFrame, size):
        sample = population_data.sample(n=min(int(size),
                                              len(population_data))).reset_index()

        sample = self._add_sample_info_columns(sample)
        sample = self._format_sample_columns(sample)

        self._save_sample_and_deliverable(sample)

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
        data = self._filter_data(data=data, data_col='ENTITY_ID',
                                 filter_data=aims_data.no_contacts, filter_col='entity_id')
        return data

    def _filter_recent_phones(self, data: pd.DataFrame):
        previous_n_months_data = self._archive.get_sample_data_past_n_months(self._months_phone_block)
        data = self._filter_data(data=data, data_col='TELEPHONE_NUMBER',
                                 filter_data=previous_n_months_data, filter_col='telephone_number')
        return data

    def _filter_recent_me(self, data: pd.DataFrame):
        previous_n_months_data = self._archive.get_sample_data_past_n_months(self._months_me_block)
        data = self._filter_data(data=data, data_col='ME',
                                 filter_data=previous_n_months_data, filter_col='me')
        return data

    @classmethod
    def _filter_data(cls, data: pd.DataFrame, data_col: str,
                     filter_data: pd.DataFrame, filter_col: str) -> pd.DataFrame:
        result = data[~data[data_col].isin(filter_data[filter_col])]
        return result

    @classmethod
    def _add_pe_description(cls, data: pd.DataFrame, aims_data: AIMSData):
        data = data.merge(aims_data.pe_descriptions, left_on='PE_CD', right_on='present_emp_cd', how='left')
        return data

    def _add_sample_info_columns(self, data):
        sample_id = self._archive.get_latest_sample_id() + 1

        data['SAMPLE_ID'] = sample_id
        data['ROW_ID'] = data.index + 1
        data['SURVEY_TYPE'] = self._survey_type
        data['SURVEY_MONTH'] = self._survey_date.month
        data['SURVEY_YEAR'] = self._survey_date.year
        data['SAMPLE_SOURCE'] = 'MF'

        return data

    def _format_sample_columns(self, data):
        data.columns = [col.upper() for col in data.columns.values]  # uppercase DataFrame column names

        cols = [col.upper() for col in self._target_sample_vars]  # target sample file column names

        data.rename(columns={'PREFERRED_PHONE_COMM_ID': 'PHONE_COMM_ID'}, inplace=True)  # expected name in the DB table

        # re-orders DataFrame columns to match order specified in self._target_sample_vars
        sample = pd.DataFrame()
        for col in cols:
            sample[col] = data[col]

        return sample

    def _save_sample_and_deliverable(self, sample):
        LOGGER.info('ADDING SAMPLE TO DATABASE')
        self._load_sample_to_archive(sample)

        self._make_deliverable_sample(sample)

    def _make_deliverable_sample(self, sample):
        deliverable = sample.drop(columns=['SURVEY_TYPE', 'SURVEY_MONTH', 'SURVEY_YEAR', 'SAMPLE_SOURCE',
                                           'PHONE_COMM_ID', 'ENTITY_ID', 'POLO_COMM_ID'])
        sample_name = f'\\{self._today_date}_Masterfile_Random_Sample.xlsx'
        sample_save_path = self._save_dir + sample_name
        writer = pd.ExcelWriter(sample_save_path, engine='xlsxwriter')

        LOGGER.info('SAVING SAMPLE TO {}'.format(sample_save_path))
        deliverable.to_excel(excel_writer=writer, index=None)
        writer.save()

    def _load_sample_to_archive(self, sample):
        self._archive.ingest_sample_data(sample)
