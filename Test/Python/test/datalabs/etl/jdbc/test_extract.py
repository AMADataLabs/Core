import os

import jaydebeapi
import pytest

from datalabs.etl.jdbc.extract import JDBCExtractor
import datalabs.etl.task as task


# @pytest.mark.skip(reason="Input Credentials")
def test_jdbc_connection(components):
    etl = task.ETLTask(components)

    parameters = etl.run()
    extractor = JDBCExtractor(parameters)
    dataframes_list = extractor._extract()

    assert dataframes_list[0].columns[0] == 'ME_NUMBER'


@pytest.fixture
def components():
    return task.ETLParameters(
        extractor=task.ETLComponentParameters(
            database=dict(
                NAME='eprdods',
                PORT='54150',
                HOST='rdbp1190',
                username='dlabs',
                password='L@bs2020'
            ),
            variables=dict(CLASS='test.datalabs.etl.jdbc.test_extract.JDBCExtractor',
                           thing=True,
                           SQL='SELECT * FROM ODS.ODS_PPD_FILE LIMIT 20;',
                           DRIVER='com.ibm.db2.jcc.DB2Driver',
                           TYPE='db2',
                           JAR_PATH='./db2jcc4.jar')
        ),
        transformer=task.ETLComponentParameters(
            database={},
            variables=None
        ),
        loader=task.ETLComponentParameters(
            database={},
            variables=None
        )
    )


@pytest.fixture
def environment_variables():
    current_env = os.environ.copy()

    os.environ['EXTRACTOR_CLASS'] = 'test.datalabs.etl.jdbc.test_extract.JDBCExtractor'
    os.environ['EXTRACTOR_DATABASE_NAME'] = 'eprdods'
    os.environ['EXTRACTOR_DATABASE_USERNAME'] = 'dlabs'
    os.environ['EXTRACTOR_DATABASE_PASSWORD'] = 'L@bs2020'
    os.environ['EXTRACTOR_DATABASE_HOST'] = 'rdbp1190'
    os.environ['EXTRACTOR_DATABASE_PORT'] = '54150'

    os.environ['EXTRACTOR_SQL'] = 'SELECT * FROM ODS.ODS_PPD_FILE LIMIT 20;'
    os.environ['EXTRACTOR_DRIVER'] = 'com.ibm.db2.jcc.DB2Driver'
    os.environ['EXTRACTOR_TYPE'] = 'db2'
    os.environ['EXTRACTOR_JAR_PATH'] = './db2jcc4.jar'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_env)
