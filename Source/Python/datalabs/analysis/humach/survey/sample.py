import pandas as pd
import os
from datetime import datetime
import logging
logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

from datalabs.analysis.humach.survey.archive import HumachResultsArchive
from datalabs.access.aims import AIMS

from filter_bad_phones import get_good_bad_phones

import settings


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
        next_months = {
            0: 1,
            1: 2,
            2: 3,
            3: 4,
            4: 5,
            5: 6,
            6: 7,
            7: 8,
            8: 9,
            9: 10,
            10: 11,
            11: 12,
            12: 1
        }
        self._survey_month = next_months[self._today_date.month]
        self._survey_year = self._today_date.year
        if self._survey_month == 1:
            self._survey_year += 1

        self.data = pd.DataFrame()

    def _set_environment_variables(self):
        self._save_dir = os.environ.get('SAVE_DIR')
        self._ppd_filename = os.environ.get('EXPANDED_PPD_FILE')
        self._archive = HumachResultsArchive(os.environ.get('SURVEY_DB_PATH'))
        self._target_sample_vars = self._archive.sample_cols
        self._months_me_block = os.environ.get('MONTHS_ME_BLOCK')
        self._months_phone_block = os.environ.get('MONTHS_PHONE_BLOCK')
        self._sample_size = os.environ.get('SAMPLE_SIZE')

    @classmethod
    def _filter_data(cls,
                     data: pd.DataFrame,
                     data_col: str,
                     filter_data: pd.DataFrame,
                     filter_col: str) -> pd.DataFrame:
        result = data[~data[data_col].isin(filter_data[filter_col])]
        return result

    def _get_sample_population_data(self) -> pd.DataFrame:
        LOGGER.info('READING PPD')
        ppd = pd.read_csv(self._ppd_filename, dtype=str)
        LOGGER.info('FILTERING TO DPC AND POPULATED PHONES')
        ppd = ppd[~ppd['TELEPHONE_NUMBER'].isna()]  # must have phone number
        ppd = ppd[ppd['TOP_CD'] == '020']  # filter to DPC
        LOGGER.info('QUERYING AIMS FOR NO-CONTACTS AND PE DESCRIPTION')
        with AIMS() as aims:
            no_contacts = aims.get_no_contacts()
            pe_descriptions = aims.get_pe_descriptions()
        # remove no-contacts
        LOGGER.info('REMOVING NO-CONTACTS')
        ppd = self._filter_data(data=ppd, data_col='ENTITY_ID',
                                filter_data=no_contacts, filter_col='entity_id')
        # filter ME numbers found in previous N months of surveys
        LOGGER.info('FILTERING OUT ME NUMBERS FOUND IN RECENT SAMPLES')
        previous_n_months_data = self._archive.get_sample_data_past_n_months(self._months_me_block)
        ppd = self._filter_data(data=ppd, data_col='ME',
                                filter_data=previous_n_months_data, filter_col='me')
        # filter phone numbers found in previous N months of surveys
        LOGGER.info('FILTERING OUT PHONE NUMBERS FOUND IN RECENT SAMPLES')
        previous_n_months_data = self._archive.get_sample_data_past_n_months(self._months_phone_block)
        ppd = self._filter_data(data=ppd, data_col='TELEPHONE_NUMBER',
                                filter_data=previous_n_months_data, filter_col='telephone_number')
        # add pe-description
        LOGGER.info('ADDING PE DESCRIPTION')
        ppd = ppd.merge(pe_descriptions, left_on='PE_CD', right_on='present_emp_cd', how='left')
        # filter out invalid numbers
        LOGGER.info('REMOVING INVALID PHONE NUMBERS')
        _, ppd = get_good_bad_phones(ppd, phone_var_name='TELEPHONE_NUMBER')

        return ppd

    def _make_sample(self, population_data: pd.DataFrame, size) -> pd.DataFrame:
        data = population_data.sample(n=min(int(size), len(population_data))).reset_index()
        data.columns = [col.upper() for col in data.columns.values]
        cols = [col.upper() for col in self._target_sample_vars]

        sample_id = self._archive.get_latest_sample_id() + 1
        data['SAMPLE_ID'] = sample_id
        data['ROW_ID'] = data.index + 1
        data['SURVEY_TYPE'] = self._survey_type
        data['SURVEY_MONTH'] = self._survey_month
        data['SURVEY_YEAR'] = self._survey_year
        data['SAMPLE_SOURCE'] = 'MF'

        data.rename(columns={'PREFERRED_PHONE_COMM_ID': 'PHONE_COMM_ID'}, inplace=True)

        sample = pd.DataFrame()
        for col in cols:
            sample[col] = data[col]

        return sample

    def _load_sample_to_archive(self, sample):
        self._archive.ingest_sample_data(sample)

    def run(self):
        LOGGER.info('SETTING VARIABLES AND CONNECTIONS')
        self._set_environment_variables()
        LOGGER.info('CREATING POPULATION DATA')
        population_data = self._get_sample_population_data()
        LOGGER.info('CREATING SAMPLE')
        sample = self._make_sample(population_data, size=self._sample_size)
        deliverable = sample.drop(columns=['SURVEY_TYPE', 'SURVEY_MONTH', 'SURVEY_YEAR', 'SAMPLE_SOURCE',
                                           'PHONE_COMM_ID', 'ENTITY_ID', 'POLO_COMM_ID'])

        sample_name = f'\\{self._today_date}_Masterfile_Random_Sample.xlsx'

        sample_save_path = self._save_dir + sample_name
        writer = pd.ExcelWriter(sample_save_path, engine='xlsxwriter')
        LOGGER.info('ADDING SAMPLE TO DATABASE')
        self._load_sample_to_archive(sample)
        LOGGER.info('SAVING SAMPLE TO {}'.format(sample_save_path))
        deliverable.to_excel(excel_writer=writer, index=None)
        writer.save()


