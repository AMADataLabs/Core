""" source: datalabs.etl.jdbc.extract """
import os

import pytest

from   datalabs.etl.jdbc.extract import JDBCExtractorTask
import datalabs.etl.task as task


# pylint: disable=redefined-outer-name, protected-access
@pytest.mark.skip(reason="Integration test. Input Credentials")
def test_jdbc_connection(components):
    extractor = JDBCExtractorTask(components)
    dataframes_list = extractor._extract()

    assert dataframes_list[0].columns[0] == 'ME_NUMBER'


@pytest.fixture
def components():
    return dict(
        DATABASE_NAME='eprdods',
        DATABASE_PORT='54150',
        DATABASE_HOST='rdbp1190',
        DATABASE_USERNAME=os.getenv('EXTRACTOR__DATABASE_USERNAME'),
        DATABASE_PASSWORD=os.getenv('EXTRACTOR__DATABASE_PASSWORD'),
        TASK_CLASS='test.datalabs.etl.jdbc.test_extract.JDBCExtractor',
        thing=True,
        SQL='SELECT * FROM ODS.ODS_PPD_FILE LIMIT 1;',
        DRIVER='com.ibm.db2.jcc.DB2Jcc',
        DRIVER_TYPE='db2',
        JAR_PATH='./db2jcc4.jar'
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

    os.environ['EXTRACTOR__SQL'] = 'SELECT * FROM ODS.ODS_PPD_FILE LIMIT 1;'
    os.environ['EXTRACTOR__DRIVER'] = 'com.ibm.db2.jcc.DB2Jcc'
    os.environ['EXTRACTOR__DRIVER_TYPE'] = 'db2'
    os.environ['EXTRACTOR__JAR_PATH'] = './db2jcc4.jar'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_env)
