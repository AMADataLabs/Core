""" Base classes for loading data from files. """
from   datetime import datetime
from   enum import Enum
import logging
from   pathlib import Path
import re
from   typing import Iterable

import pandas as pd

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class DataFileType(Enum):
    CSV = 'csv'
    EXCEL = 'xslx'
    EXCEL_OLD = 'xlsm'


class DataFile:
    @classmethod
    def load_multiple(cls, files: Iterable, file_type: DataFileType = None) -> pd.DataFrame:
        dataset = []

        for file in files:
            data = cls.load(file, file_type)

            dataset.append(data)

        return pd.concat(dataset, ignore_index=True)

    @classmethod
    def load(cls, file: str, file_type: DataFileType = None) -> pd.DataFrame:
        file_type = file_type or cls._intuit_file_type(file)
        data_date = cls._extract_date_from_path(file)

        data = cls._load_from_file(file, file_type)

        data = cls._standardize(data, data_date)

        return data

    @classmethod
    def _intuit_file_type(cls, path):
        path = Path(path)
        extension = path.name.rsplit('.', 1)[1]
        file_type = DataFileType.CSV

        try:
            file_type = DataFileType(extension)
        except ValueError:
            pass

        return file_type

    @classmethod
    def _extract_date_from_path(cls, path):
        path = Path(path)
        datestamp = cls._extract_datestamp_from_filename(path.name)
        date = None

        if datestamp:
            date = datetime.strptime(datestamp, '%Y-%m-%d')

        return date

    @classmethod
    def _load_from_file(cls, file_name, file_type: DataFileType):
        data = None

        if file_type == DataFileType.CSV:
            data = pd.read_csv(file_name, index_col=None, header=0, dtype=str)
        elif file_type == DataFileType.EXCEL:
            data = pd.read_excel(file_name, index_col=None, header=0, dtype=str)

        return data

    @classmethod
    def _standardize(cls, data: pd.DataFrame, data_date: datetime) -> pd.DataFrame:  # pylint: disable=unused-argument
        return data

    @classmethod
    def _extract_datestamp_from_filename(cls, filename):
        datestamp = None
        match = re.match(r'.+([1-9][0-9]{3}-[0-1][0-9]-[0-3][0-9])', filename)

        if match:
            datestamp = match.group(1)

        return datestamp or cls._extract_dense_datestamp_from_filename(filename)

    @classmethod
    def _extract_dense_datestamp_from_filename(cls, filename):
        datestamp = None
        match = re.match(r'.+([1-9][0-9]{3})([0-1][0-9])([0-3][0-9])', filename)

        if match:
            datestamp = f'{match.group(1)}-{match.group(2)}-{match.group(3)}'

        return datestamp
