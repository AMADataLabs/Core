""" source: datalabs.etl.fs.extract """
import logging
import os
import tempfile

import mock
import pytest

from datalabs.plugin import import_plugin

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


# pylint: disable=redefined-outer-name, protected-access
def test_data_setup_correctly(extractor_file):
    with open(extractor_file) as file:
        data = file.read()

    LOGGER.debug('Input Data: %s', data)
    assert len(data) > 0


# pylint: disable=redefined-outer-name, protected-access
def test_extractor_loads_correct_file(etl):
    with mock.patch('datalabs.access.parameter.boto3'):
        etl.run()

    extractor = etl._task._extractor

    assert len(extractor.data) > 0


@pytest.fixture
def extractor_directory():
    with tempfile.TemporaryDirectory() as temp_directory:
        yield temp_directory


# pylint: disable=redefined-outer-name, line-too-long
@pytest.fixture
def extractor_file(extractor_directory):
    prefix = 'PhysicianProfessionalDataFile_2020120'

    with tempfile.NamedTemporaryFile(dir=extractor_directory, prefix=prefix+'1'):
        with tempfile.NamedTemporaryFile(dir=extractor_directory, prefix=prefix+'2') as file:
            file.write(
                """We all live in a yellow submarine...""".encode('UTF-8')
            )
            file.flush()

            yield file.name


# pylint: disable=redefined-outer-name, unused-argument
@pytest.fixture
def environment(extractor_file):
    current_environment = os.environ.copy()

    os.environ['TASK_WRAPPER_CLASS'] = 'datalabs.etl.task.ETLTaskWrapper'
    os.environ['TASK_CLASS'] = 'datalabs.etl.task.ETLTask'

    os.environ['EXTRACTOR_CLASS'] = 'datalabs.etl.fs.extract.LocalUnicodeTextFileExtractorTask'
    os.environ['EXTRACTOR_BASEPATH'] = os.path.dirname(extractor_file)
    os.environ['EXTRACTOR_FILES'] = 'PhysicianProfessionalDataFile_*'

    os.environ['TRANSFORMER_CLASS'] = 'datalabs.etl.transform.PassThroughTransformerTask'

    os.environ['LOADER_CLASS'] = 'datalabs.etl.load.ConsoleLoaderTask'

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
