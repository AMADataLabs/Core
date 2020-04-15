""" Class for loading data from PPD files. """
# pylint: disable=R0801
from datetime import datetime
import logging

import pandas as pd

import datalabs.curate.dataframe  # pylint: disable=unused-import
from datalabs.access.file import DataFile

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class PPDFile(DataFile):
    @classmethod
    def _standardize(cls, data: pd.DataFrame, data_date: datetime) -> pd.DataFrame:
        data = data.datalabs.rename_in_upper_case()

        data['PPD_DATE'] = data_date

        return data
