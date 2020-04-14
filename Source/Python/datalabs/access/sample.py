from datetime import datetime, timedelta
import logging

import pandas as pd

import datalabs.curate.dataframe as df
from datalabs.access.file import DataFile

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class SampleFile(DataFile):
    @classmethod
    def _extract_date_from_file_name(cls, file):
        slash_ndx = [i for i in range(len(file)) if file.startswith('/', i)]
        base_name = file[slash_ndx[-1] + 1:]
        under_ndx = base_name.find('_')
        dash_ndx = base_name.find('-')
        date_str = base_name[dash_ndx + 1:under_ndx]

        return datetime.strptime(date_str, '%Y-%m-%d')

    @classmethod
    def _standardize(cls, data: pd.DataFrame, data_date: datetime) -> pd.DataFrame:
        data = df.rename_in_upper_case(data)

        data['SAMPLE_DATE'] = data_date
        data['SAMPLE_MAX_DATE'] = data_date + timedelta(months=2)

        return data
