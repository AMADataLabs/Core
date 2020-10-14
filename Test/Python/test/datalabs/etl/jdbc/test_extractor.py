import os

import jaydebeapi
import pytest

from datalabs.etl.jdbc.extractor import JDBCExtractor
import datalabs.etl.task as task


@pytest.mark.skip(reason="Input Credentials")
def test_jdbc_connection(parameters):
    dataframes_dict = JDBCExtractor._extract()

    assert list(dataframes_dict.keys())[0] == 'ODS.ODS_PPD_FILE'


@pytest.fixture
def parameters():
    return task.ETLParameters(
        extractor=task.ETLComponentParameters(
            database={},
            variables=dict(CLASS='test.datalabs.etl.jdbc.test_extract.Extractor', thing=True)
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

    os.environ['EXTRACTOR_DATABASE_NAME'] = 'eprdods'
    os.environ['EXTRACTOR_DATABASE_USERNAME'] = ''
    os.environ['EXTRACTOR_DATABASE_PASSWORD'] = ''
    os.environ['EXTRACTOR_DATABASE_HOST'] = 'rdbp1190.ama-assn.org'
    os.environ['EXTRACTOR_DATABASE_PORT'] = '54150'

    os.environ['EXTRACTOR_SQL'] = 'SELECT * FROM ODS.ODS_PPD_FILE;'
    os.environ['EXTRACTOR_DRIVER'] = 'com.ibm.db2.jcc.DB2Jcc'
    os.environ['EXTRACTOR_TYPE'] = 'db2'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_env)


