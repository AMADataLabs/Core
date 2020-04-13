from datetime import datetime
import logging

import pandas as pd

import datalabs.curate.dataframe as df
from datalabs.access.file import DataFile

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PPDFile(DataFile):
    @classmethod
    def _extract_date_from_file_name(cls, file_name):
        under_ndx = under_ndx = [i for i in range(len(file_name)) if file_name.startswith('_', i)]
        dot_ndx = file_name.find('.')
        ppd_date_str = file_name[under_ndx[-1] + 1:dot_ndx]

        return datetime.datetime.strptime(ppd_date_str, '%Y%m%d')

    @classmethod
    def _standardize(cls, data: pd.DataFrame, data_date: datetime) -> pd.DataFrame:
        data = df.rename_in_upper_case(data)

        data['PPD_DATE'] = data_date

        return data
