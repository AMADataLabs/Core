""" source: datalabs.etl.fs.extract """
import logging
import os

import mock
import pytest

import datalabs.etl.fs.extract as fs
from   datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_data_setup_correctly(extractor_file):
    with open(extractor_file, encoding="utf-8") as file:
        data = file.read()

    LOGGER.debug('Input Data: %s', data)
    assert len(data) > 0


# pylint: disable=redefined-outer-name, protected-access
def test_extractor_loads_correct_file(etl):
    with mock.patch('datalabs.access.parameter.aws.boto3'):
        etl.run()

    assert len(etl.task._output.extractor) > 0


# pylint: disable=redefined-outer-name, protected-access
def test_whitespace_removed_from_filenames(parameters):
    task = fs.LocalFileExtractorTask(parameters)

    files = task._get_files()

    assert len(files) == 3
    assert files[2] == 'dir1/dir2/dir3/the_other_one.csv'


def test_cp1252_decoding(parameters):
    task = fs.LocalWindowsTextFileExtractorTask(parameters)
    cp1252_encoded_text = '¥'.encode('cp1252')
    unicode_encoded_text = task._decode_data(cp1252_encoded_text)

    assert unicode_encoded_text == '¥'.encode("utf-8")


# pylint: disable=redefined-outer-name, unused-argument
@pytest.fixture
def environment(extractor_file):
    current_environment = os.environ.copy()

    os.environ['TASK_WRAPPER_CLASS'] = 'datalabs.etl.task.ETLTaskWrapper'
    os.environ['TASK_CLASS'] = 'datalabs.etl.task.ETLTask'

    os.environ['EXTRACTOR__TASK_CLASS'] = 'datalabs.etl.fs.extract.LocalFileExtractorTask'
    os.environ['EXTRACTOR__BASE_PATH'] = os.path.dirname(extractor_file)
    os.environ['EXTRACTOR__FILES'] = 'PhysicianProfessionalDataFile_*'

    os.environ['TRANSFORMER__TASK_CLASS'] = 'datalabs.etl.transform.PassThroughTransformerTask'

    os.environ['LOADER__TASK_CLASS'] = 'datalabs.etl.load.ConsoleLoaderTask'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)


# pylint: disable=redefined-outer-name
@pytest.fixture
def etl(environment):
    task_wrapper_class = import_plugin(environment.get('TASK_WRAPPER_CLASS'))
    task_wrapper = task_wrapper_class(parameters={})

    return task_wrapper


@pytest.fixture
def parameters():
    return dict(
        BASE_PATH='dir1/dir2/dir3',
        FILES='this_one.csv,that_one.csv,\n       the_other_one.csv     ',
        EXECUTION_TIME='19000101'
    )
