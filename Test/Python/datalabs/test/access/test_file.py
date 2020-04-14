from collections import namedtuple
from datetime import datetime

import pytest

from datalabs.access.file import DataFile


def test_extract_date_from_filename(path_dataset):
    for path_data in path_dataset:
        date = DataFile._extract_date_from_path(path_data.name)

        assert path_data.date == date


FileData = namedtuple('FileData', 'name date')


@pytest.fixture
def path_dataset():
    return [
        FileData(
            "/mnt/u/Source Files/Data Analytics/Data-Science/Data/k-2019-08-23_Standard_Sample.xlsx",
            datetime(2019, 8, 23)
        ),
        FileData(
            "U:/Source Files/Data Analytics/Data-Science/Data/k-2019-09-23_Masterfile_Model_Sample.xlsx",
            datetime(2019, 9, 23)
        ),
        FileData(
            "U:\\Source Files\\Data Analytics\\Data-Science\\Data\\k-2019-10-31_Masterfile_Model_Sample_Source_CB.xlsx",
            datetime(2019, 10, 31)
        ),
        FileData(
            "/mnt/u/Source Files/Data Analytics/Data-Science/Data/WSLive/Reports/p-WSLive-Results-20190612.xlsm",
            datetime(2019, 6, 12)
        ),
        FileData(
            "U:/Source Files/Data Analytics/Data-Science/Data/WSLive/Reports/p-WSLive-Results-20190716.xlsm",
            datetime(2019, 7, 16)
        ),
        FileData(
            "U:\\Source Files\\Data Analytics\\Data-Science\\Data\\WSLive\\Reports\\p-WSLive-Results-20190816.xlsm",
            datetime(2019, 8, 16)
        ),
        FileData(
            "/mnt/u/Source Files/Data Analytics/Data-Science/Data/WSLive/wslive_with_results_2019-01-04_to_2019-08-23",
            datetime(2019, 8, 23)
        ),
    ]
