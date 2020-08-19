from dataclasses import dataclass
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
import os
import pandas as pd

from datalabs.access.aims import AIMS
from datalabs.access.edw import EDW, PartyKeyType
from datalabs.analysis.vertical_trail.physician_contact.archive import VTPhysicianContactArchive

import settings

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


@dataclass
class AIMSData:
    no_contacts: pd.DataFrame = pd.DataFrame()
    pe_descriptions: pd.DataFrame = pd.DataFrame()
    active_licenses: pd.DataFrame = pd.DataFrame()
    specialty_descriptions: pd.DataFrame = pd.DataFrame()
    entity_comm_phone_data: pd.DataFrame = pd.DataFrame()

@dataclass
class EDWData:
    medschool_names: pd.DataFrame = pd.DataFrame()
    party_key_data: pd.DataFrame = pd.DataFrame()


class VTPhysicianContactSampleGenerator:
    def __init__(self, archive: VTPhysicianContactArchive = None, survey_type: str = None):
        self._survey_type = survey_type
        self._target_sample_vars = []

        self._sample_size = None
        self._save_dir = None
        self._archive = archive
        self._ppd_filename = None

        self.aims_data = AIMSData()
        self.edw_data = EDWData()

        """ Exclusion time periods """
        self._months_me_block = None
        self._months_phone_block = None

        """ Date """
        self._today_date = datetime.now().date()
        self._survey_date = self._today_date + relativedelta(months=1)

    def run(self):
        LOGGER.info('SETTING VARIABLES AND CONNECTIONS')
        self._load_environment_variables()
        self._load_database_data()
        LOGGER.info('CREATING POPULATION DATA')
        population_data = self._get_population_data()
        LOGGER.info('CREATING SAMPLE')
        self._make_sample(population_data, size=self._sample_size)


    def _load_environment_variables(self):
        self._save_dir = os.environ.get('SAVE_DIR')
        self._ppd_filename = os.environ.get('EXPANDED_PPD_FILE')
        self._archive = VTPhysicianContactArchive(os.environ.get('ARCHIVE_DB_PATH'))
        self._target_sample_vars = self._archive.expected_file_columns.samples
        self._target_deliverable_columns = self._archive.expected_file_columns.samples
        self._months_me_block = os.environ.get('MONTHS_ME_BLOCK')
        self._sample_size = os.environ.get(f'SAMPLE_SIZE_VERTICAL_TRAIL')

    def _load_database_data(self):
        self._load_aims_data()
        self._load_edw_data()

    def _get_population_data(self):
        ppd = self._load_ppd()

        data = self._prepare_population_data(data=ppd)
        return data

    def _make_sample(self, population_data: pd.DataFrame, size):
        sample = population_data.sample(n=min(int(size), len(population_data))).reset_index()
        sample = self._add_old_phone_data(sample=sample)

        sample = self._add_sample_info_columns(sample)
        sample = self._format_sample_columns(sample)

        #self._archive.ingest_vt_sample(sample)  # not yet implemented
        self._make_deliverable_sample(sample)

    def _load_ppd(self):
        ppd = pd.read_csv(self._ppd_filename, dtype=str)
        return ppd

    def _load_aims_data(self):
        aims_data = AIMSData()
        with AIMS() as aims:
            aims_data.no_contacts = aims.get_no_contacts()
            aims_data.pe_descriptions = aims.get_pe_descriptions()
            aims_data.active_licenses = aims.get_active_licenses()
            aims_data.specialty_descriptions = aims.get_specialty_descriptions()
            aims_data.entity_comm_phone_data = aims.get_entity_comm_phones()
        self.aims_data = aims_data

    @classmethod
    def _load_edw_data(cls):
        edw_data = EDWData()
        with EDW() as edw:
            edw_data.medschool_names = edw.get_active_medical_school_map()
            edw_data.party_key_data = edw.get_party_keys_by_type(party_key_type=PartyKeyType.School)
        return edw_data

    def _prepare_population_data(self, data: pd.DataFrame):
        data = self._filter_to_dpc(data=data)
        LOGGER.info('filter_dpc', len(data))
        data = self._filter_to_no_phone(data=data)
        LOGGER.info('filter_no_phone', len(data))
        data = self._filter_no_contacts(data=data)
        LOGGER.info('filter_no_contacts', len(data))
        data = self._filter_recent_me(data=data)
        LOGGER.info('filter_recent_me', len(data))
        data = self._add_license_info(data=data)
        LOGGER.info('add_license_info', len(data))
        data = self._add_medschool_data(data=data)
        LOGGER.info('add_medschool_data', len(data))
        data = self._add_degree_and_specialty_data(data=data)
        LOGGER.info('add_degree_and_specialty_data', len(data))
        data = self._get_deduped_physician_medschool_data(data)
        LOGGER.info('get_deduped_physician_medschool_data', len(data))
        return data

    def _add_license_info(self, data):
        license_data = self.aims_data.active_licenses.sort_values(
            'lic_exp_dt',
            ascending=False
        ).groupby('entity_id').first().reset_index()
        license_data['entity_id'] = license_data['entity_id'].astype(str)
        data = data.merge(license_data, left_on='ENTITY_ID', right_on='entity_id', how='inner')
        return data

    def _add_medschool_data(self, data):
        data['medschool_key'] = data['MEDSCHOOL_STATE'] + data['MEDSCHOOL_ID']
        data.rename(columns={'PARTY_ID': 'PHYSICIAN_PARTY_ID'}, inplace=True)

        data = data.merge(
            self.edw_data.party_key_data,
            how='inner',
            left_on='medschool_key',
            right_on='KEY_VAL'
        )
        self.edw_data.medschool_names.rename(columns={'PARTY_ID': 'MEDSCHOOL_PARTY_ID'}, inplace=True)

        data = data.merge(self.edw_data.medschool_names, left_on='PARTY_ID', right_on='MEDSCHOOL_PARTY_ID', how='inner')

        return data

    def _add_degree_and_specialty_data(self, data: pd.DataFrame):
        data['degree_type'] = 'MD'
        do_ndx = data['MD_DO_CODE'] == 2
        data.loc[do_ndx, 'degree_type'] = 'DO'

        data = data.merge(
            self.aims_data.specialty_descriptions,
            left_on='PRIM_SPEC_CD',
            right_on='spec_cd',
            how='inner'
        )
        data.rename(columns={'description': 'spec_description'}, inplace=True)
        data['specialty'] = data['spec_description']
        return data

    @classmethod
    def _get_deduped_physician_medschool_data(cls, data: pd.DataFrame):
        data = data.groupby(
            ['FIRST_NAME',
             'LAST_NAME',
             'MEDSCHOOL_GRAD_YEAR',
             'state_cd'
             ]
        ).apply(lambda x: x.sample(1)).reset_index(drop=True)
        return data

    def _add_old_phone_data(self, sample: pd.DataFrame):
        filtered_entity_comm_data = self.aims_data.entity_comm_phone_data[
            self.aims_data.entity_comm_phone_data['entity_id'].isin(sample['entity_id'])
        ]
        filtered_entity_comm_data = filtered_entity_comm_data.sort_values(
            ['entity_id', 'aims_phone']
        ).groupby(
            ['entity_id', 'aims_phone']
        ).first().reset_index()
        filtered_entity_comm_data['aims_phone'] = filtered_entity_comm_data['aims_phone'].astype(str)
        filtered_entity_comm_data['aims_phone'] = filtered_entity_comm_data['aims_phone'].apply(
            lambda x: ''.join(x.split())
        )
        entity_ids = filtered_entity_comm_data['entity_id'].drop_duplicates().values

        old_phone_data, old_phone_columns = self._get_old_phone_data(
            historical_phone_data=filtered_entity_comm_data,
            entity_ids=entity_ids
        )
        sample = sample.merge(old_phone_data, on='entity_id', how='left')
        return sample

    def _get_old_phone_data(self, historical_phone_data, entity_ids):
        """ Disgusting old function from common code. It works and will take some time to clean up. """
        temp_phone_dict = self._get_temp_phone_dict(historical_phone_data, entity_ids)
        max_phones = temp_phone_dict['max']
        del temp_phone_dict['max']

        old_phone_data = pd.DataFrame({'entity_id': entity_ids})
        for i in range(max_phones):
            name = 'oldphone' + str((i + 1))
            old_phone_data[name] = ''

        for entity_id in temp_phone_dict.keys():
            phone_list = temp_phone_dict[entity_id]['old_phones']
            entity_id_index = old_phone_data[old_phone_data['entity_id'] == entity_id].index[0]

            for i in range(len(phone_list)):
                phone = phone_list[i]
                name = 'oldphone' + str(i + 1)
                old_phone_data.loc[entity_id_index, name] = phone

        oldphone_name_list = ['oldphone' + str(i + 1) for i in range(max_phones)]
        return old_phone_data, oldphone_name_list

    def _get_temp_phone_dict(self, historical_phone_data, entity_ids):
        temp_phone_dict = {}
        max_phones = 0  # the maximum number of old phones found for any one individual
        for i in range(len(entity_ids)):
            temp_df = historical_phone_data[historical_phone_data['entity_id'] == entity_ids[i]]
            temp_phones = list(temp_df['aims_phone'])

            num_phones = len(temp_phones)
            if num_phones > max_phones:
                max_phones = num_phones

            temp_phone_dict[entity_ids[i]] = {}
            temp_phone_dict[entity_ids[i]]['num_phones'] = len(temp_phones)
            temp_phone_dict[entity_ids[i]]['old_phones'] = temp_phones

        temp_phone_dict['max'] = max_phones
        return temp_phone_dict

    def _add_sample_info_columns(self, data):
        latest_sample_id = self._archive.get_latest_sample_id()
        if latest_sample_id is None:
            latest_sample_id = 0
        sample_id = latest_sample_id + 1
        data['SAMPLE_ID'] = sample_id
        data['ROW_ID'] = data.index + 1
        data['SAMPLE_DATE'] = self._today_date
        return data

    def _format_sample_columns(self, data: pd.DataFrame):
        data.columns = [col.upper() for col in data.columns.values]
        data.rename(
            columns={
                'STATE_CD': 'LIC_STATE'
            },
            inplace=True
        )
        cols = [col.upper() for col in self._archive.table_columns.samples]  # column names required for archive table

        # re-orders DataFrame columns to match order specified in self._target_sample_vars
        sample = pd.DataFrame()
        for col in cols:
            sample[col] = data[col]
        return sample

    def _filter_to_no_phone(self, data: pd.DataFrame):
        data = data[data['TELEPHONE_NUMBER'].isna()]
        return data

    @classmethod
    def _filter_to_dpc(cls, data: pd.DataFrame):
        data = data[data['TOP_CD'] == '020']
        return data

    def _filter_no_contacts(self, data: pd.DataFrame):
        data = self._filter_data(
            data=data,
            data_col='ENTITY_ID',
            filter_data=self.aims_data.no_contacts,
            filter_col='entity_id'
        )
        return data

    def _filter_recent_me(self, data: pd.DataFrame):
        previous_n_months_data = self._archive.get_vt_sample_data_past_n_months(self._months_me_block)
        data = self._filter_data(
            data=data,
            data_col='ME',
            filter_data=previous_n_months_data,
            filter_col='me'
        )
        return data

    def _add_pe_description(self, data: pd.DataFrame):
        data = data.merge(self.aims_data.pe_descriptions, left_on='PE_CD', right_on='present_emp_cd', how='left')
        return data

    def _load_sample_to_archive(self, sample):
        #self._archive.ingest_vt_sample(sample)
        pass

    def _make_deliverable_sample(self, sample):
        deliverable = sample.drop(
            columns=[
                'ME',
                'SAMPLE_DATE'
            ]
        )
        deliverable.columns = self._archive.expected_file_columns.samples

        sample_name = f'\\{self._today_date}_VT_Physician_Contact_Sample.xlsx'
        sample_save_path = self._save_dir + sample_name
        writer = pd.ExcelWriter(sample_save_path, engine='xlsxwriter')

        LOGGER.info('SAVING SAMPLE TO {}'.format(sample_save_path))
        deliverable.to_excel(excel_writer=writer, index=None)
        writer.save()

    @classmethod
    def _filter_data(cls, data: pd.DataFrame, data_col: str, filter_data: pd.DataFrame, filter_col: str):
        return data[~data[data_col].isin(filter_data[filter_col])]

