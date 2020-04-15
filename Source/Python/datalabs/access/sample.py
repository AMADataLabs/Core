''' Class for loading data from sample files. '''

from datetime import datetime
import logging

from dateutil.relativedelta import relativedelta
import pandas as pd

import datalabs.curate.dataframe  # pylint: disable=unused-import
from datalabs.access.file import DataFile

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class SampleFile(DataFile):
    @classmethod
    def _standardize(cls, data: pd.DataFrame, data_date: datetime) -> pd.DataFrame:
        data = data.datalabs.rename_in_upper_case()

        data['SAMPLE_DATE'] = data_date
        data['SAMPLE_MAX_DATE'] = data_date + relativedelta(months=2)

        return data
