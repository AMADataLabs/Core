''' Class for loading data from sample files. '''

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

import pandas as pd

import datalabs.curate.dataframe as df
from datalabs.access.file import DataFile

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class SampleFile(DataFile):
    @classmethod
    def _standardize(cls, data: pd.DataFrame, data_date: datetime) -> pd.DataFrame:
        data = df.rename_in_upper_case(data)

        data['SAMPLE_DATE'] = data_date
        data['SAMPLE_MAX_DATE'] = data_date + relativedelta(months=2)

        return data
