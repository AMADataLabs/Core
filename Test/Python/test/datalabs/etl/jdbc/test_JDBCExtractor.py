import os

import jaydebeapi
import pytest

from datalabs.etl.jdbc.jdbc_extractor import JDBCExtractor


@pytest.mark.skip(reason="Input Credentials")
def test_jdbc_connection(environment):
    dataframes_dict = JDBCExtractor.jdbc_connect()

    assert list(dataframes_dict.keys())[0] == 'ODS.ODS_PPD_FILE'


@pytest.fixture
def environment():
    os.environ['PATH_TO_DRIVER_JAR'] = '--jars file:postgresql-42.2.16.jar'
    os.environ['EXTRACTOR_SQL'] = 'SELECT * FROM ODS.ODS_PPD_FILE;'
    os.environ['DATABASE_ODS_USERNAME'] = ''
    os.environ['DATABASE_ODS_PASSWORD'] = ''


