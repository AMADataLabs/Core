""" source: datalabs.etl.fs.load """
from datetime import datetime
from glob import glob
import logging
import os
import tempfile

import mock
import pytest

import datalabs.etl.fs.load as fs
from datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name
def test_data_setup_correctly(extractor_file):
    with open(extractor_file) as file:
        data = file.read()

    LOGGER.debug('Input Data: %s', data)
    assert len(data) > 0


# pylint: disable=redefined-outer-name, protected-access
def test_loader_loads_two_files(etl, loader_directory):
    with mock.patch('datalabs.access.parameter.aws.boto3'):
        etl.run()

    data = etl.task._loader._parameters['data']

    LOGGER.debug('Loaded Data: %s', data)
    assert len(data) == 2

    files = glob(os.path.join(loader_directory, '*'))
    assert len(files) == 2


# pylint: disable=redefined-outer-name
def test_loader_properly_adds_datestamp(etl, loader_directory):
    with mock.patch('datalabs.access.parameter.aws.boto3'):
        etl.run()

    files = sorted(glob(os.path.join(loader_directory, '*')), key=len)
    expected_filename = datetime.utcnow().strftime('PhysicianProfessionalDataFile_%Y-%m-%d.csv')
    expected_path = os.path.join(loader_directory, expected_filename)
    assert expected_path == files[1]


# pylint: disable=redefined-outer-name, protected-access
def test_whitespace_removed_from_filenames(parameters):
    task = fs.LocalFileLoaderTask(parameters)

    files = task._get_files()

    assert len(files) == 3
    assert files[2] == 'dir1/dir2/dir3/the_other_one.csv'


@pytest.fixture
def loader_directory():
    with tempfile.TemporaryDirectory() as temp_directory:
        yield temp_directory


# pylint: disable=redefined-outer-name
@pytest.fixture
def environment(extractor_file, loader_directory):
    current_environment = os.environ.copy()

    os.environ['TASK_WRAPPER_CLASS'] = 'datalabs.etl.task.ETLTaskWrapper'
    os.environ['TASK_CLASS'] = 'datalabs.etl.task.ETLTask'

    os.environ['EXTRACTOR__TASK_CLASS'] = 'datalabs.etl.fs.extract.LocalUnicodeTextFileExtractorTask'
    os.environ['EXTRACTOR__BASE_PATH'] = os.path.dirname(extractor_file)
    os.environ['EXTRACTOR__FILES'] = 'PhysicianProfessionalDataFile_*'
    os.environ['EXTRACTOR__INCLUDE_NAMES'] = 'True'

    os.environ['TRANSFORMER__TASK_CLASS'] = 'test.datalabs.etl.fs.transform.FilenameStripperTransformerTask'

    os.environ['LOADER__TASK_CLASS'] = 'datalabs.etl.fs.load.LocalUnicodeTextFileLoaderTask'
    os.environ['LOADER__BASE_PATH'] = loader_directory
    os.environ['LOADER__FILES'] = 'PhysicianProfessionalDataFile.csv,PhysicianProfessionalDataFile_%Y-%m-%d.csv'

    yield os.environ

    os.environ.clear()
    os.environ.update(current_environment)


# pylint: disable=redefined-outer-name
@pytest.fixture
def etl(environment):
    task_class = import_plugin(environment.get('TASK_CLASS'))
    task_wrapper_class = import_plugin(environment.get('TASK_WRAPPER_CLASS'))
    task_wrapper = task_wrapper_class(task_class, parameters={})

    return task_wrapper


@pytest.fixture
def parameters():
    return dict(
        BASE_PATH='dir1/dir2/dir3',
        FILES='this_one.csv,that_one.csv,\n       the_other_one.csv     ',
        EXECUTION_TIME='19000101'
    )
