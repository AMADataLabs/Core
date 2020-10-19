import logging
import os
import pytest

import datalabs.etl.task as task
from   datalabs.etl.oneview.ppd.transform import PPDDataFramesToCSVText

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


@pytest.mark.skip(reason="")
def test_jdbc_connection(parameters):
    csv_list = PPDDataFramesToCSVText._transform()

    assert csv_list[0].split(',')[0] == 'ME_NUMBER'


@pytest.fixture
def parameters():
    return task.ETLParameters(
        extractor=task.ETLComponentParameters(
            database={},
            variables=dict(CLASS='test.datalabs.etl.jdbc.test_extract.Extractor', thing=True)
        ),
        transformer=task.ETLComponentParameters(
            database={},
            variables=dict(CLASS='datalabs.etl.oneview.ppd.transform.PPDDataFramesToCSVText', thing=True)
        ),
        loader=task.ETLComponentParameters(
            database={},
            variables=None
        )
    )


@pytest.fixture
def environment(extractor_file, loader_directory):
    current_environment = os.environ.copy()

    os.environ['TASK_WRAPPER_CLASS'] = 'datalabs.etl.task.ETLTaskWrapper'
    os.environ['TASK_CLASS'] = 'datalabs.etl.task.ETLTask'

    os.environ['EXTRACTOR_CLASS'] = 'datalabs.etl.jdbc.JDBCExtractor'

    os.environ['TRANSFORMER_CLASS'] = 'datalabs.etl.oneview.ppd.transform.PPDDataFramesToCSVText'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)
