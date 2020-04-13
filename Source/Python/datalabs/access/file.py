from abc import ABC
from datetime import datetime, timedelta
import logging
from typing import Iterable

import pandas as pd

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class DataFile:
    @classmethod
    def load_multiple(cls, files: Iterable) -> pd.DataFrame:
        dataset = []

        for file in files:
            data = cls.load(file)
            
            dataset.append(data)

        return pd.concat(dataset, ignore_index=True)

    @classmethod
    def load(cls, file: str) -> pd.DataFrame:
        data_date = _extract_date_from_file_name(file)

        data = cls._load_from_file(file)

        data = cls._standardize(data, data_date)

        return data

    @classmethod
    def _extract_date_from_file_name(cls, file_name):
        return datetime.now()

    @classmethod
    def _load_from_file(cls, file_name):
        return pd.read_csv(file_name, index_col=None, header=0, dtype=str)

    @classmethod
    def _standardize(cls, data: pd.DataFrame, data_date: datetime) -> pd.DataFrame:
        return data
