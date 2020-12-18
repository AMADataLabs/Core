""" source: datalabs.etl.jdbc.extract """
import os

import pytest

from   datalabs.etl.jdbc.extract import JDBCExtractorTask
import datalabs.etl.task as task


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.skip(reason="Integration test. Input Credentials")
def test_jdbc_connection(components):
    extractor = JDBCExtractor(components)
    dataframes_list = extractor._extract()

    assert dataframes_list[0].columns[0] == 'ME_NUMBER'


@pytest.fixture
def components():
    return task.ETLComponentParameters(
        database=dict(
            NAME='eprdods',
            PORT='54150',
            HOST='rdbp1190',
            username=os.getenv('EXTRACTOR_DATABASE_USERNAME'),
            password=os.getenv('EXTRACTOR_DATABASE_PASSWORD')
        ),
        variables=dict(
            CLASS='test.datalabs.etl.jdbc.test_extract.JDBCExtractor',
            thing=True,
            SQL='SELECT * FROM ODS.ODS_PPD_FILE LIMIT 1;',
            DRIVER='com.ibm.db2.jcc.DB2Jcc',
            DRIVER_TYPE='db2',
            JAR_PATH='./db2jcc4.jar')
        )


@pytest.fixture
def environment_variables():
    current_env = os.environ.copy()

    os.environ['EXTRACTOR_CLASS'] = 'test.datalabs.etl.jdbc.test_extract.JDBCExtractor'
    os.environ['EXTRACTOR_DATABASE_NAME'] = 'eprdods'
    # os.environ['EXTRACTOR_DATABASE_USERNAME'] = <set manually in environment>
    # os.environ['EXTRACTOR_DATABASE_PASSWORD'] = <set manually in environment>
    os.environ['EXTRACTOR_DATABASE_HOST'] = 'rdbp1190'
    os.environ['EXTRACTOR_DATABASE_PORT'] = '54150'

    os.environ['EXTRACTOR_SQL'] = 'SELECT * FROM ODS.ODS_PPD_FILE LIMIT 1;'
    os.environ['EXTRACTOR_DRIVER'] = 'com.ibm.db2.jcc.DB2Jcc'
    os.environ['EXTRACTOR_DRIVER_TYPE'] = 'db2'
    os.environ['EXTRACTOR_JAR_PATH'] = './db2jcc4.jar'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_env)
