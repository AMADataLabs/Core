import pandas as pd
import os
from glob import glob

import settings


class ExpandedPPDLoader:
    def __init__(self):
        self._raw_dir = None
        self._save_dir = None
        self._archive_dir = None

        self._columns = [
            'ME',
            'PARTY_ID',
            'ENTITY_ID',
            'RECORD_ID',
            'UPDATE_TYPE',
            'ADDRESS_TYPE',
            'MAILING_NAME',
            'LAST_NAME',
            'FIRST_NAME',
            'MIDDLE_NAME',
            'SUFFIX',
            'PPMA_POST_CD_ID',
            'PPMA_COMM_ID',
            'MAILING_LINE_1',
            'MAILING_LINE_2',
            'CITY',
            'STATE',
            'ZIP',
            'SECTOR',
            'CARRIER_ROUTE',
            'ADDRESS_UNDELIVERABLE_FLAG',
            'FIPS_COUNTY',
            'FIPS_STATE',
            'PRINTER_CONTROL_CODE',
            'PC_ZIP',
            'PC_SECTOR',
            'DELIVERY_POINT_CODE',
            'CHECK_DIGIT',
            'PRINTER_CONTROL_CODE_2',
            'REGION',
            'DIVISION',
            'GROUP',
            'TRACT',
            'SUFFIX_CENSUS',
            'BLOCK_GROUP',
            'MSA_POPULATION_SIZE',
            'MICRO_METRO_IND',
            'CBSA',
            'CBSA_DIV_IND',
            'MD_DO_CODE',
            'BIRTH_YEAR',
            'BIRTH_CITY',
            'BIRTH_STATE',
            'BIRTH_COUNTRY',
            'GENDER',
            'PREFERRED_PHONE_PHONE_ID',
            'PREFERRED_PHONE_COMM_ID',
            'TELEPHONE_NUMBER',
            'PRESUMED_DEAD_FLAG',
            'PREFERRED_FAX_PHONE_ID',
            'PREFERRED_FAX_COMM_ID',
            'FAX_NUMBER',
            'TOP_CD',
            'PE_CD',
            'PRIM_SPEC_CD',
            'SEC_SPEC_CD',
            'MPA_CD',
            'PRA_RECIPIENT',
            'PRA_EXP_DT',
            'GME_CONF_FLG',
            'FROM_DT',
            'TO_DT',
            'YEAR_IN_PROGRAM',
            'POST_GRADUATE_YEAR',
            'GME_SPEC_1',
            'GME_SPEC_2',
            'TRAINING_TYPE',
            'GME_INST_STATE',
            'GME_INST_ID',
            'MEDSCHOOL_STATE',
            'MEDSCHOOL_ID',
            'MEDSCHOOL_GRAD_YEAR',
            'NO_CONTACT_IND',
            'NO_WEB_FLAG',
            'PDRP_FLAG',
            'PDRP_START_DT',
            'POLO_POST_CD_ID',
            'POLO_COMM_ID',
            'POLO_MAILING_LINE_1',
            'POLO_MAILING_LINE_2',
            'POLO_CITY',
            'POLO_STATE',
            'POLO_ZIP',
            'POLO_SECTOR',
            'POLO_CARRIER_ROUTE',
            'MOST_RECENT_FORMER_LAST_NAME',
            'MOST_RECENT_FORMER_MIDDLE_NAME',
            'MOST_RECENT_FORMER_FIRST_NAME',
            'NEXT_MOST_RECENT_FORMER_LAST',
            'NEXT_MOST_RECENT_FORMER_MIDDLE',
            'NEXT_MOST_RECENT_FORMER_FIRST'
    ]

    def run(self):
        self._load_environment_variables()
        # print(self._raw_dir)
        latest_raw_file = self._get_latest_file(dir=self._raw_dir, extension='txt')
        latest_raw_date = self._get_file_date(latest_raw_file)
        latest_loaded_file = self._get_latest_file(dir=self._archive_dir, extension='csv')
        latest_loaded_date = self._get_file_date(latest_loaded_file)
        # if there is no archived file or if there is a newer raw file than we've got already
        if latest_loaded_file is None or latest_raw_date > latest_loaded_date:
            data = self._load_data(latest_raw_file)
            self._save_data(data=data, filename=latest_raw_file)

    def _load_environment_variables(self):
        self._raw_dir = os.environ.get('RAW_DIR')
        self._save_dir = os.environ.get('SAVE_DIR')
        self._archive_dir = os.environ.get('ARCHIVE_DIR')

    @classmethod
    def _get_latest_file(cls, dir, extension) -> str:
        latest_file = None
        files = glob(dir + f'/*.{extension}')
        if len(files) > 0:
            latest_file = sorted(files)[-1]
        return latest_file

    @classmethod
    def _get_file_date(cls, filename: str):
        date = None
        if filename is not None:
            date = filename[filename.rindex('_') + 1:filename.rindex('.')]
            date = pd.to_datetime(date).date()
        return date

    def _load_data(self, filename: str):
        return pd.read_csv(
            filename,
            sep='|',
            dtype=str,
            encoding='LATIN',
            names=self._columns,
            index_col=False
        )

    def _save_data(self, data, filename):
        filename = filename[filename.rindex('\\') + 1:].replace('.txt', '.csv')  # archive version w/ date
        filename_dateless = filename[:filename.rindex('_')] + '.csv'  # removes date
        # print(filename, filename_dateless)
        save_path = f"{self._save_dir}\\{filename_dateless}"  # newest file name will be persistent
        archive_path = f"{self._archive_dir}\\{filename}"
        # print(save_path, archive_path)
        data.to_csv(save_path, index=False)
        data.to_csv(archive_path, index=False)
