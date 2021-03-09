""" source: datalabs.etl.cpt.extract """
from   datetime import date
import io
import logging

import mock
import pytest

import pandas

from   datalabs.etl.cpt.ingest.extract import CPTTextDataExtractorTask

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_datestamp_conversion():
    datestamps = ['1-Jan', '15-Dec', '13-Mar']
    expected_dates = [date(1900, 1, 1), date(1900, 12, 15), date(1900, 3, 13)]
    dates = CPTTextDataExtractorTask._convert_datestamps_to_dates(datestamps)

    for expected_date, actual_date in zip(expected_dates, dates):
        assert actual_date == expected_date


@mock.patch('datalabs.etl.cpt.ingest.extract.CPTTextDataExtractorTask._get_latest_path')
# pylint: disable=redefined-outer-name, protected-access
def test_extract_release_date(get_latest_path, task_parameters):
    with mock.patch('datalabs.access.aws.boto3'):
        get_latest_path.return_value = 'AMA/CPT/20200131'
        extractor = CPTTextDataExtractorTask(task_parameters)
        expected_release_date = '20200131'
        release_date = extractor._extract_release_date()

    assert get_latest_path.call_count == 1
    assert release_date == expected_release_date

# pylint: disable=redefined-outer-name, protected-access
def test_generate_release_types(release_schedule, task_parameters):
    with mock.patch('datalabs.access.aws.boto3'):
        extractor = CPTTextDataExtractorTask(task_parameters)
        release_types = extractor._generate_release_types(release_schedule)

    assert len(release_types.columns.values) == 1
    assert 'type' in release_types
    assert len(release_types) == 6
    assert release_types.type.to_list() == ['ANNUAL', 'Q1', 'Q2', 'Q3', 'Q4', 'OTHER']

# pylint: disable=redefined-outer-name, protected-access
def test_get_release_type(release_schedule, task_parameters):
    with mock.patch('datalabs.access.aws.boto3'):
        extractor = CPTTextDataExtractorTask(task_parameters)
        release_date = date(2020, 7, 1)
        expected_release_type = 'Q3'
        release_type = extractor._get_release_type(release_schedule, release_date)

    assert release_type == expected_release_type

# pylint: disable=redefined-outer-name, protected-access
def test_generate_release_details(release_schedule, task_parameters):
    with mock.patch('datalabs.access.aws.boto3'):
        extractor = CPTTextDataExtractorTask(task_parameters)
        release_date = date(2020, 7, 1)
        effective_date = date(2020, 10, 1)
        release_details = pandas.read_csv(
            io.StringIO(extractor._generate_release_details(release_schedule, release_date))
        )

    assert len(release_details.columns.values) == 3
    assert all([c in release_details for c in ['publish_date', 'effective_date', 'type']])
    assert len(release_details) == 1
    assert release_details.publish_date.iloc[0] == release_date.strftime('%Y-%m-%d')
    assert release_details.effective_date.iloc[0] == effective_date.strftime('%Y-%m-%d')
    assert release_details.type.iloc[0] == 'Q3'

@pytest.fixture
def release_schedule():
    return {
        "ANNUAL": ["1-Sep", "1-Jan"],
        "Q1": ["1-Jan", "1-Apr"],
        "Q2": ["1-Apr", "1-Jul"],
        "Q3": ["1-Jul", "1-Oct"],
        "Q4": ["1-Oct", "1-Jan"]
    }


@pytest.fixture
def task_parameters():
    return dict(
        ENDPOINT_URL='https://bogus.host.fqdn/path/file',
        ACCESS_KEY='nviowaj4902hfisafh9402fdni0ph8',
        SECRET_KEY='wr9e0afe90afohf90aw',
        REGION_NAME='us-east-42',
        BUCKET='jumanji',
        BASE_PATH='dir1/dir2/dir3',
        FILES='this_one.csv,that_one.csv,the_other_one.csv',
        EXECUTION_TIME='19000101'
    )
