""" source: datalabs.etl.jdbc.extract """
import os
import random

import mock
import pandas
import pytest

from   datalabs.etl.jdbc.extract import JDBCExtractorTask


# pylint: disable=redefined-outer-name, protected-access
def test_data_properly_converted_to_bytes_after_read(parameters):
    with mock.patch('datalabs.etl.jdbc.extract.JDBCExtractorTask._read_single_query') as read_single_query:
        extractor = JDBCExtractorTask(parameters)

        # pylint: disable=unused-argument
        def mock_read(query, connection):
            return pandas.DataFrame(dict(
                column1=random.sample(range(10, 30), 5),
                column2=random.sample(range(10, 30), 5)
            ))
        read_single_query.side_effect = mock_read

        result = extractor._read_queries(None)

        assert len(result) == 1
        assert hasattr(result[0], 'decode')


# pylint: disable=redefined-outer-name, protected-access
def test_chunked_query_not_performed_when_no_chunk_size(parameters):
    with mock.patch('datalabs.etl.jdbc.extract.JDBCExtractorTask._read_single_query') as read_single_query:
        extractor = JDBCExtractorTask(parameters)

        # pylint: disable=unused-argument
        def mock_read(query, connection):
            return pandas.DataFrame(dict(
                column1=random.sample(range(10, 30), 5),
                column2=random.sample(range(10, 30), 5)
            ))
        read_single_query.side_effect = mock_read

        result = extractor._read_query('SELECT * FROM BOGUS', None)

        assert len(result) == 5


# pylint: disable=redefined-outer-name, protected-access
def test_chunked_query_is_chunked_correctly(parameters):
    parameters['CHUNK_SIZE'] = '5'
    with mock.patch('datalabs.etl.jdbc.extract.JDBCExtractorTask._read_single_query') as read_single_query:
        extractor = JDBCExtractorTask(parameters)
        counter = 0
        max_count = 3

        # pylint: disable=unused-argument
        def mock_read(query, connection):
            nonlocal counter
            result = []

            if counter < max_count:
                result = pandas.DataFrame(dict(
                    column1=random.sample(range(10, 30), 5),
                    column2=random.sample(range(10, 30), 5)
                ))

            counter += 1

            return result
        read_single_query.side_effect = mock_read

        result = extractor._read_chunked_query('SELECT * FROM BOGUS', None)

        assert len(result) == 15


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.skip(reason="Integration test. Input Credentials")
def test_jdbc_connection(parameters):
    parameters['DATABASE_USERNAME'] = os.getenv('EXTRACTOR__DATABASE_USERNAME')
    parameters['DATABASE_PASSWORD'] = os.getenv('EXTRACTOR__DATABASE_PASSWORD')

    extractor = JDBCExtractorTask(parameters)
    dataframes_list = extractor._extract()

    assert dataframes_list[0].columns[0] == 'ME_NUMBER'


@pytest.fixture
def parameters():
    return dict(
        DATABASE_NAME='eprdods',
        DATABASE_PORT='54150',
        DATABASE_HOST='rdbp1190',
        DATABASE_USERNAME='cbarkley',
        DATABASE_PASSWORD='strongestcrewmemberofNCC1701-D',
        SQL='SELECT * FROM ODS.ODS_PPD_FILE ORDER BY ME_NUMBER LIMIT {index}, {count};',
        DRIVER='com.ibm.db2.jcc.DB2Jcc',
        DRIVER_TYPE='db2',
        JAR_PATH='./db2jcc4.jar',
    )


@pytest.fixture
def environment_variables():
    current_env = os.environ.copy()

    os.environ['EXTRACTOR__TASK_CLASS'] = 'test.datalabs.etl.jdbc.test_extract.JDBCExtractor'
    os.environ['EXTRACTOR__DATABASE_NAME'] = 'eprdods'
    # os.environ['EXTRACTOR__DATABASE_USERNAME'] = <set manually in environment>
    # os.environ['EXTRACTOR__DATABASE_PASSWORD'] = <set manually in environment>
    os.environ['EXTRACTOR__DATABASE_HOST'] = 'rdbp1190'
    os.environ['EXTRACTOR__DATABASE_PORT'] = '54150'

    os.environ['EXTRACTOR__SQL'] = 'SELECT * FROM ODS.ODS_PPD_FILE ORDER BY ME_NUMBER LIMIT {index}, {count};'
    os.environ['EXTRACTOR__DRIVER'] = 'com.ibm.db2.jcc.DB2Jcc'
    os.environ['EXTRACTOR__DRIVER_TYPE'] = 'db2'
    os.environ['EXTRACTOR__JAR_PATH'] = './db2jcc4.jar'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_env)
