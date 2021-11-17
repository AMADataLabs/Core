""" source: datalabs.etl.jdbc.extract """
import os
from   pathlib import Path
import random

import mock
import pandas
import pytest

from   datalabs.etl.jdbc.extract import JDBCExtractorTask, JDBCParametricExtractorTask, JDBCParquetExtractorTask


# pylint: disable=redefined-outer-name, protected-access
def test_data_properly_converted_to_bytes_after_read(parameters, read):
    extractor = JDBCExtractorTask(parameters)

    with mock.patch('pandas.read_sql') as read_sql:
        read_sql.side_effect = read

        result = extractor._read_queries(None)

    assert len(result) == 1
    assert hasattr(result[0], 'decode')


# pylint: disable=redefined-outer-name, protected-access
def test_chunked_query_not_performed_when_no_chunk_size(parameters, read):
    extractor = JDBCExtractorTask(parameters)

    with mock.patch('pandas.read_sql') as read_sql:
        read_sql.side_effect = read

        result = extractor._read_query('SELECT * FROM BOGUS', None)

    assert len(result) == 5


# pylint: disable=redefined-outer-name, protected-access
def test_chunked_query_is_chunked_correctly(parameters, chunked_read):
    parameters['CHUNK_SIZE'] = '5'
    extractor = JDBCExtractorTask(parameters)
    result = None

    with mock.patch('pandas.read_sql') as read_sql:
        read_sql.side_effect = chunked_read

        result = extractor._read_query('SELECT * FROM BOGUS', None)

    assert len(result) == 15


# pylint: disable=redefined-outer-name, protected-access
def test_query_results_saved_as_parquet(parameters, read):
    extractor = JDBCParquetExtractorTask(parameters)

    with mock.patch('pandas.read_sql') as read_sql:
        read_sql.side_effect = read

        result = extractor._read_query('SELECT * FROM BOGUS', None)

    assert hasattr(result, 'name')
    assert hasattr(result, 'cleanup')

    files = list(Path(result.name).glob("parquet*"))
    assert len(files) == 1

    data = pandas.read_parquet(files[0])
    assert len(data) == 5
    assert 'column1' in data
    assert 'column2' in data


# pylint: disable=redefined-outer-name, protected-access
def test_chunked_query_results_saved_as_parquet(parameters, chunked_read):
    parameters['CHUNK_SIZE'] = '5'
    extractor = JDBCParquetExtractorTask(parameters)

    with mock.patch('pandas.read_sql') as read_sql:
        read_sql.side_effect = chunked_read

        result = extractor._read_query('SELECT * FROM BOGUS', None)

    assert hasattr(result, 'name')
    assert hasattr(result, 'cleanup')

    files = list(Path(result.name).glob("parquet*"))
    assert len(files) == 3

    data_parts = []
    for path in files:
        data_parts.append(pandas.read_parquet(path))

    data = pandas.concat(data_parts)
    assert len(data) == 15
    assert 'column1' in data
    assert 'column2' in data


# pylint: disable=redefined-outer-name, protected-Access
def test_parametric_extra_resolves_query_variables(parameters, parametric_data):
    parameters['SQL'] = "SELECT * FROM some_table WHERE year = '{year}'"
    parameters['PART_INDEX'] = '1'
    parameters['MAX_PARTS'] = '3'
    parameters['data'] = [parametric_data.to_csv(index=False).encode()]
    expected_query = parameters['SQL'].format(year='2014')

    extractor = JDBCParametricExtractorTask(parameters)

    resolved_query = extractor._resolve_query(parameters['SQL'], 0, 0)
    assert expected_query == resolved_query


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
def parametric_data():
    return pandas.DataFrame(data=dict(year=['2003', '2014', '2015']))


@pytest.fixture
def read():
    # pylint: disable=unused-argument
    def read_sql(query, connection):
        return pandas.DataFrame(dict(
            column1=random.sample(range(10, 30), 5),
            column2=random.sample(range(10, 30), 5)
        ))

    return read_sql


@pytest.fixture
def chunked_read():
    counter = 0
    max_count = 3

    # pylint: disable=unused-argument
    def read_sql(query, connection):
        nonlocal counter
        result = pandas.DataFrame(columns=['column1', 'column2'])

        if counter < max_count:
            result = pandas.DataFrame(dict(
                column1=random.sample(range(10, 30), 5),
                column2=random.sample(range(10, 30), 5)
            ))

        counter += 1

        return result

    return read_sql


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
