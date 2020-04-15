""" Class for loading data from WSLive/Humach result files. """
# pylint: disable=R0801
from datetime import datetime
import logging

import pandas as pd

import datalabs.curate.dataframe as df
from datalabs.access.file import DataFile

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class WSLiveFile(DataFile):
    @classmethod
    def _standardize(cls, data: pd.DataFrame, data_date: datetime) -> pd.DataFrame:
        data = df.rename_in_upper_case(data)

        data = cls._filter_columns(data)

        data = cls._filter_for_masterfile_sourced_rows(data)

        data['WSLIVE_FILE_DT'] = pd.to_datetime(data['WSLIVE_FILE_DT'])

        return data

    @classmethod
    def _filter_columns(cls, data):
        keep_columns = [
            'PHYSICIAN_ME_NUMBER', 'OFFICE_TELEPHONE', 'OFFICE_FAX', 'OFFICE_ADDRESS_LINE_2', 'OFFICE_ADDRESS_LINE_1',
            'OFFICE_ADDRESS_CITY', 'OFFICE_ADDRESS_STATE', 'OFFICE_ADDRESS_ZIP', 'WSLIVE_FILE_DT',
            'COMMENTS', 'SPECIALTY', 'PRESENT_EMPLOYMENT_CODE', 'ADDR_STATUS', 'PHONE_STATUS', 'FAX_STATUS',
            'SPEC_STATUS', 'PE_STATUS', 'NEW_METRIC', 'PPD_DATE', 'SOURCE', 'WS_YEAR', 'WS_MONTH'
        ]

        return data[keep_columns]

    @classmethod
    def _filter_for_masterfile_sourced_rows(cls, data):
        return data[data['SOURCE'].isin(['C', 'Z', 'CR'])]
